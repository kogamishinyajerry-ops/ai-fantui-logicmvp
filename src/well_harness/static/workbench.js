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

// E11-03 R2 (P1 NIT fix, 2026-04-26): translate the internal column
// token (control/document/circuit) into the user-facing engineer-task
// verb so the failure-path copy never reverts to technical-noun
// phrasing. Mapping mirrors the rename in workbench.html.
// P44-01 (2026-04-26): the workbench is now centered on the actual
// control logic panel. The previous 3-column shell (Probe & Trace /
// Annotate & Propose / Hand off & Track) was an empty placeholder grid
// — the L1→L4 logic panel was missing entirely. bootWorkbenchShell now
// fetches the SVG fragment from /api/workbench/circuit-fragment and
// injects it into #workbench-circuit-hero-mount.
//
// The fragment endpoint extracts its content from fantui_circuit.html
// (single source of truth for the SVG), so /workbench and the static
// /fantui_circuit.html page never drift.
// P45-01 (2026-04-26): which system the hero currently displays. The
// dropdown #workbench-system-select is the single source of truth;
// changing it triggers a fragment re-fetch via reloadWorkbenchCircuitHero.
function currentWorkbenchSystem() {
  const select = document.getElementById("workbench-system-select");
  return (select && select.value) || "thrust-reverser";
}

async function bootWorkbenchCircuitHero() {
  const mount = workbenchElement("workbench-circuit-hero-mount");
  if (!mount) {
    return;
  }
  const endpointBase =
    mount.getAttribute("data-circuit-fragment-endpoint") ||
    "/api/workbench/circuit-fragment";
  const system = currentWorkbenchSystem();
  const endpoint = `${endpointBase}?system=${encodeURIComponent(system)}`;
  // Mark which system the SVG belongs to so review-mode + interpreter
  // can stay in sync if either runs before the fetch resolves.
  mount.setAttribute("data-circuit-system", system);
  try {
    const response = await fetch(endpoint, { headers: { Accept: "text/html" } });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const fragment = await response.text();
    if (!fragment.includes("<svg ")) {
      throw new Error("response missing <svg>");
    }
    // Per-system gate sanity-check: only the wired thrust-reverser
    // is required to carry L1..L4. Placeholder SVGs from
    // unwired systems are intentionally gate-less and pass through.
    if (system === "thrust-reverser") {
      for (const gateId of ["L1", "L2", "L3", "L4"]) {
        if (!fragment.includes(`data-gate-id="${gateId}"`)) {
          throw new Error(`fragment missing data-gate-id="${gateId}"`);
        }
      }
    }
    mount.innerHTML = fragment;
    mount.setAttribute("data-circuit-fragment-status", "ready");
    mount.setAttribute(
      "aria-label",
      `${system} SVG circuit (loaded)`,
    );
    // P44-04: re-apply review anchors against the freshly hydrated SVG
    // so that if the inbox already loaded (race with this fetch) and we
    // computed gate→count, the badges show up the instant the SVG
    // appears. Safe no-op if review mode is off, proposals empty, or
    // the new fragment carries no gate anchors (placeholder system).
    applyReviewAnchors(_latestProposals);
    // P55-03: paint always-on fan-in count badges. Structural fact
    // (input arity) — runs once per hydration, not per proposal
    // refresh. Safe no-op when the fragment carries no
    // data-input-count anchors (placeholder + c919 systems).
    applyGateFanInBadges();
  } catch (error) {
    mount.setAttribute("data-circuit-fragment-status", "error");
    mount.innerHTML =
      `<p class="workbench-circuit-hero-error" role="alert">` +
      `控制逻辑面板加载失败 · Failed to load control logic panel: ` +
      `${error.message || error}. ` +
      `请直接打开 <a href="/fantui_circuit.html">/fantui_circuit.html</a> ` +
      `查看静态版本 · open the static circuit page directly.` +
      `</p>`;
  }
}

// P45-01 (2026-04-26): re-fetch + re-render the hero for the
// currently-selected system. Wired to the dropdown's `change` event
// so toggling system in the topbar re-paints the panel without a
// page reload. Idempotent — calling it twice is fine, the second
// fetch just races and the latest one wins.
async function reloadWorkbenchCircuitHero() {
  const mount = document.getElementById("workbench-circuit-hero-mount");
  if (!mount) return;
  // Reset state so the loading affordance shows up while the new
  // fragment is in flight.
  mount.setAttribute("data-circuit-fragment-status", "pending");
  mount.innerHTML =
    `<p class="workbench-circuit-hero-loading">` +
    `正在加载控制逻辑面板… · Loading control logic panel…` +
    `</p>`;
  await bootWorkbenchCircuitHero();
}

function bootWorkbenchShell() {
  // Fire-and-forget: the hero hydrates asynchronously so the rest of the
  // workbench chrome (topbar, state-of-world bar, approval center)
  // renders immediately without waiting on the fragment request.
  bootWorkbenchCircuitHero();
  installSuggestionFlow();
  installProposalInbox();
  installReviewModeToggle();
  installPanelVersionChip();
  installSystemSelectorReload();
}

// P45-01 (2026-04-26): wire the system dropdown so changing the
// selection re-fetches the circuit fragment for the new system.
// P45-02 (2026-04-26): also re-loads the proposals inbox scoped to
// the new system so the engineer sees only that system's tickets.
function installSystemSelectorReload() {
  const select = document.getElementById("workbench-system-select");
  if (!select) return;
  select.addEventListener("change", () => {
    reloadWorkbenchCircuitHero();
    loadProposalsInbox();
  });
}

// P45-02 (2026-04-26): mirror the current system in the inbox
// header so the engineer always knows which system's tickets are
// in front of them. Single DOM mutation per refresh; safe to call
// every load.
function refreshInboxHeaderForSystem(system) {
  const header = document.querySelector("#annotation-inbox header h2");
  if (!header) return;
  header.textContent = `审核队列 · Review Queue · ${system}`;
}

// ─────────────────────────────────────────────────────────────────
// P44-02 (2026-04-26): suggestion-input flow.
// Engineer types a free-form modification suggestion, the server
// interprets it via /api/workbench/interpret-suggestion, the UI
// highlights the interpreted gate(s) on the SVG, the engineer
// confirms the interpretation matches intent, then submits the ticket.
// ─────────────────────────────────────────────────────────────────

const SUGGESTION_INTERPRET_PATH = "/api/workbench/interpret-suggestion";

let _lastInterpretation = null;

function installSuggestionFlow() {
  const form = document.getElementById("workbench-suggestion-form");
  const interpretBtn = document.getElementById("workbench-suggestion-interpret-btn");
  const reinterpretBtn = document.getElementById("workbench-suggestion-reinterpret-btn");
  const cancelBtn = document.getElementById("workbench-suggestion-cancel-btn");
  const confirmBtn = document.getElementById("workbench-suggestion-confirm-btn");
  if (!form || !interpretBtn) {
    return;  // not on /workbench
  }
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    runSuggestionInterpret();
  });
  if (reinterpretBtn) {
    reinterpretBtn.addEventListener("click", () => runSuggestionInterpret());
  }
  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => clearSuggestionInterpretation());
  }
  if (confirmBtn) {
    confirmBtn.addEventListener("click", () => onConfirmClicked());
  }
  // P54-09 (2026-04-28): wire draft autosave + restore + conflict-banner buttons.
  installSuggestionDraftRestore();
  const proceedBtn = document.getElementById("workbench-suggestion-conflict-proceed");
  const conflictCancelBtn = document.getElementById("workbench-suggestion-conflict-cancel");
  if (proceedBtn) {
    proceedBtn.addEventListener("click", () => {
      // Pull the system snapshot the banner was rendered with —
      // proceed must file under the same system_id we conflict-
      // checked, even if the user has since flipped the dropdown.
      const banner = document.getElementById("workbench-suggestion-conflict-banner");
      const sysId = banner ? banner.getAttribute("data-system-snapshot") : null;
      hideConflictBanner();
      submitSuggestionTicket(sysId || undefined);
    });
  }
  if (conflictCancelBtn) {
    conflictCancelBtn.addEventListener("click", () => hideConflictBanner());
  }
  // P45-03 (2026-04-26): wire the interpreter strategy toggle. Off
  // (rules) → on (llm) → off … flips the chip's data attribute and
  // label; runSuggestionInterpret reads the chip on send so the
  // toggle takes effect on the next 解读 click.
  const strategyChip = document.getElementById("workbench-interpreter-strategy-toggle");
  if (strategyChip) {
    strategyChip.addEventListener("click", () => toggleInterpreterStrategy());
  }
}

// P45-03 (2026-04-26): flip the interpreter strategy. The chip's
// data-interpreter-strategy attribute is the source of truth read by
// runSuggestionInterpret; this function only mutates DOM.
function toggleInterpreterStrategy() {
  const chip = document.getElementById("workbench-interpreter-strategy-toggle");
  if (!chip) return;
  const next = chip.getAttribute("data-interpreter-strategy") === "llm" ? "rules" : "llm";
  chip.setAttribute("data-interpreter-strategy", next);
  chip.setAttribute("aria-pressed", next === "llm" ? "true" : "false");
  const label = chip.querySelector("[data-interpreter-strategy-label]");
  if (label) {
    label.textContent = next === "llm"
      ? "🤖 智能解读 · AI"
      : "📜 规则解读 · Rules";
  }
}

function currentInterpreterStrategy() {
  const chip = document.getElementById("workbench-interpreter-strategy-toggle");
  return (chip && chip.getAttribute("data-interpreter-strategy")) || "rules";
}

async function runSuggestionInterpret() {
  const input = document.getElementById("workbench-suggestion-input");
  const status = document.getElementById("workbench-suggestion-status");
  if (!input || !status) {
    return;
  }
  const text = (input.value || "").trim();
  if (!text) {
    status.dataset.status = "error";
    status.textContent = "请先输入建议内容 · enter a suggestion first";
    return;
  }
  // P45-03: read current strategy + current system from their
  // single sources of truth so the request is fully self-describing.
  const strategy = currentInterpreterStrategy();
  const system_id = currentWorkbenchSystem();
  // Codex round-2 P2-2: tear down any stale conflict banner from
  // a prior interpretation. Otherwise the banner's "继续提交" button
  // would still call submitSuggestionTicket on the NEW _lastInterpretation,
  // misleading the user about which conflict set they're bypassing.
  hideConflictBanner();
  status.dataset.status = "loading";
  status.textContent = strategy === "llm"
    ? "🤖 LLM 解读中… · interpreting via LLM…"
    : "解读中… · interpreting…";
  try {
    const response = await fetch(SUGGESTION_INTERPRET_PATH, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, strategy, system_id }),
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const interpretation = await response.json();
    _lastInterpretation = interpretation;
    renderSuggestionInterpretation(interpretation);
    // P59-03: highlight all addressable nodes — gates + input signals
    // + named output cmds. summaries is optional and not yet emitted
    // by the interpreter (kept in the API for future expansion).
    highlightSuggestionNodes({
      gates: interpretation.affected_gates || [],
      signals: interpretation.target_signals || [],
      outputs: interpretation.affected_outputs || [],
      summaries: [],
    });
    status.dataset.status = "success";
    status.textContent = "解读完成，请确认 · interpretation ready, please confirm";
  } catch (error) {
    status.dataset.status = "error";
    status.textContent = `解读失败 · interpret failed: ${error.message || error}`;
  }
}

function renderSuggestionInterpretation(interpretation) {
  const card = document.getElementById("workbench-suggestion-interpretation");
  if (!card) {
    return;
  }
  card.hidden = false;
  card.dataset.state = "ready";
  // P45-03: surface which interpreter actually produced this result
  // so the engineer can tell "via rules", "via LLM", or "LLM
  // unavailable — using rules" without parsing the JSON themselves.
  const strategyBadge = document.getElementById("workbench-suggestion-interpretation-strategy");
  if (strategyBadge) {
    const strategy = interpretation.interpreter_strategy || "rules";
    strategyBadge.dataset.interpreterStrategy = strategy;
    if (strategy === "llm") {
      strategyBadge.textContent = `🤖 via ${interpretation.llm_model || "LLM"}`;
    } else if (strategy === "llm_fallback_to_rules") {
      const why = interpretation.llm_error || "unknown";
      strategyBadge.textContent = `⚠ LLM unavailable (${why}) — fell back to rules`;
    } else {
      strategyBadge.textContent = "📜 via rules";
    }
  }
  const setText = (id, value) => {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = value || "—";
    }
  };
  setText(
    "workbench-suggestion-interpretation-gates",
    (interpretation.affected_gates || []).join(", ") || "(未识别 · none identified)",
  );
  setText(
    "workbench-suggestion-interpretation-change-kind",
    interpretation.change_kind_zh && interpretation.change_kind_en
      ? `${interpretation.change_kind_zh} · ${interpretation.change_kind_en}`
      : interpretation.change_kind_en || "(未识别 · none identified)",
  );
  setText(
    "workbench-suggestion-interpretation-targets",
    (interpretation.target_signals || []).join(", ") || "(未识别 · none identified)",
  );
  // P59-03: surface affected_outputs (output cmd names mentioned
  // directly in the user's text — distinct from the parent gate).
  // Falls back to "—" when the field is absent (older server).
  setText(
    "workbench-suggestion-interpretation-outputs",
    (interpretation.affected_outputs || []).join(", ") || "(未识别 · none identified)",
  );
  setText(
    "workbench-suggestion-interpretation-summary",
    interpretation.summary_zh || interpretation.summary_en || "(无 · empty)",
  );
  renderRecommendedWorkOrder(interpretation);
  const conf = document.getElementById("workbench-suggestion-interpretation-confidence");
  if (conf) {
    const c = typeof interpretation.confidence === "number" ? interpretation.confidence : 0;
    conf.dataset.confidence = String(c);
    conf.textContent = `置信度 · confidence: ${(c * 100).toFixed(0)}%`;
  }
  renderConfidenceBreakdown(interpretation);
}

// P54-09 (2026-04-28): render the per-component confidence breakdown
// (gate / signal / change-kind) as 3 mini bars + an optional
// vocabulary-hint reveal explaining "why uncertain" when something
// came up empty. The backend ships confidence_breakdown + vocabulary_hint
// alongside the existing fields; we degrade gracefully if either is
// missing (older server, or LLM stripped them).
function renderConfidenceBreakdown(interpretation) {
  const wrap = document.getElementById("workbench-suggestion-confidence-breakdown");
  if (!wrap) return;
  const breakdown = (interpretation && interpretation.confidence_breakdown) || {};
  const hint = (interpretation && interpretation.vocabulary_hint) || {};
  // Map component → both Chinese + English in the hint text.
  const labels = {
    gate: { zh: "门", en: "gate" },
    signal: { zh: "信号", en: "signal" },
    change_kind: { zh: "变更动词", en: "change verb" },
  };
  let anyData = false;
  for (const component of ["gate", "signal", "change_kind"]) {
    const row = wrap.querySelector(`[data-component="${component}"]`);
    if (!row) continue;
    const value = typeof breakdown[component] === "number" ? breakdown[component] : 0;
    const fill = row.querySelector(".workbench-suggestion-confidence-bar-fill");
    const pct = row.querySelector(".workbench-suggestion-confidence-pct");
    if (fill) {
      const widthPct = Math.round(value * 100);
      fill.style.width = widthPct + "%";
      fill.dataset.fill = String(value);
    }
    if (pct) {
      pct.textContent = Math.round(value * 100) + "%";
      pct.dataset.pct = String(Math.round(value * 100));
    }
    row.dataset.met = value > 0 ? "true" : "false";
    if (typeof breakdown[component] === "number") anyData = true;
  }
  // Build the hint when at least one dimension came up empty.
  const hintEl = document.getElementById("workbench-suggestion-confidence-hint");
  if (hintEl) {
    const lines = [];
    for (const component of ["gate", "signal", "change_kind"]) {
      const list = hint[component];
      if (!Array.isArray(list) || list.length === 0) continue;
      const lab = labels[component];
      const sample = list.slice(0, 8);
      const more = list.length > 8 ? `、…（+${list.length - 8}）` : "";
      const tags = sample.map((v) => `<strong>${escapeHtml(String(v))}</strong>`).join("、");
      lines.push(
        `💡 ${lab.zh}（${lab.en}）未识别 — 试试 · try one of: ${tags}${more}`
      );
    }
    if (lines.length > 0) {
      hintEl.innerHTML = lines.join("<br>");
      hintEl.hidden = false;
    } else {
      hintEl.innerHTML = "";
      hintEl.hidden = true;
    }
  }
  wrap.dataset.state = anyData ? "ready" : "empty";
}

function escapeHtml(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// P59-03 (2026-04-29): generalized highlight chain.
// Original P44-01 highlightSuggestionGates only matched [data-gate-id]
// (L1..L4). After P59-01 added per-signal anchors (data-signal-id /
// data-summary-id) and P59-02 surfaced affected_outputs from the
// interpreter, the workbench can now glow ANY logic node — not just
// the four gates. highlightSuggestionNodes is the new entry point;
// highlightSuggestionGates is preserved as a thin alias so any
// external caller keeps working.
// P59-03 (2026-04-29): render the recommended work-order draft
// produced by the P59-02 engine extension. The draft is template-
// driven on the server (recommended_work_order_zh / _en) and stays in
// the response payload regardless of LLM strategy. Hidden when no
// draft is present (pre-P59-02 server, or both fields empty).
function renderRecommendedWorkOrder(interpretation) {
  const wrap = document.getElementById("workbench-suggestion-recommendation");
  if (!wrap) return;
  const textEl = document.getElementById("workbench-suggestion-recommendation-text");
  if (!textEl) return;
  const draft =
    (interpretation && interpretation.recommended_work_order_zh) ||
    (interpretation && interpretation.recommended_work_order_en) ||
    "";
  // Codex P59-03 NIT-02: always reset to collapsed before each
  // render. Without this, an engineer who expanded the draft on a
  // prior interpretation would see the next one already open.
  // ↻ 重新解读 calls runSuggestionInterpret() directly (not
  // clearSuggestionInterpretation), so the reset has to live here.
  wrap.removeAttribute("open");
  if (!draft) {
    wrap.hidden = true;
    textEl.textContent = "";
    return;
  }
  textEl.textContent = draft;
  wrap.hidden = false;
}

// P59-03: bind the "复制" / Copy button. Uses navigator.clipboard
// when available, falls back to a transient textarea otherwise.
// Wired once on DOMContentLoaded (same lifecycle as the rest of the
// workbench install* handlers).
// Codex P59-03 NIT-01: rapid clicks must not capture a transient
// label as "original" and leave the button stuck in copied state. Use
// a constant idle label, cancel any pending reset timer before
// scheduling a new one, and treat execCommand returning false as a
// failure (legacy contexts where copy is denied).
const RECOMMENDATION_COPY_IDLE_LABEL = "📋 复制 · Copy";
let _recommendationCopyResetTimer = null;

function installRecommendationCopyHandler() {
  const btn = document.getElementById(
    "workbench-suggestion-recommendation-copy-btn",
  );
  if (!btn) return;
  btn.addEventListener("click", async () => {
    const textEl = document.getElementById(
      "workbench-suggestion-recommendation-text",
    );
    if (!textEl || !textEl.textContent) return;
    let copied = false;
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(textEl.textContent);
        copied = true;
      } else {
        // Fallback for older browsers / non-secure contexts.
        const ta = document.createElement("textarea");
        ta.value = textEl.textContent;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        copied = document.execCommand("copy") === true;
        document.body.removeChild(ta);
      }
    } catch (_err) {
      copied = false;
    }
    btn.textContent = copied
      ? "✓ 已复制 · Copied"
      : "复制失败 · Copy failed";
    if (_recommendationCopyResetTimer !== null) {
      clearTimeout(_recommendationCopyResetTimer);
    }
    _recommendationCopyResetTimer = setTimeout(() => {
      btn.textContent = RECOMMENDATION_COPY_IDLE_LABEL;
      _recommendationCopyResetTimer = null;
    }, 1500);
  });
}

function highlightSuggestionNodes(options) {
  const mount = document.getElementById("workbench-circuit-hero-mount");
  if (!mount) {
    return;
  }
  const opts = options || {};
  const gates = Array.isArray(opts.gates) ? opts.gates : [];
  const signals = Array.isArray(opts.signals) ? opts.signals : [];
  const outputs = Array.isArray(opts.outputs) ? opts.outputs : [];
  const summaries = Array.isArray(opts.summaries) ? opts.summaries : [];

  // Clear any previous highlight (covers all 3 attribute kinds since
  // the CSS selector already does — single classList sweep is enough).
  for (const el of mount.querySelectorAll(".is-suggestion-target")) {
    el.classList.remove("is-suggestion-target");
  }
  // Apply new highlights. Per the P59-01 schema, an input signal can
  // appear in multiple gate columns (engine_running × 3, tra_deg × 2);
  // querySelectorAll matches all instances so the visual feedback
  // shows every place in the diagram where the signal lives.
  for (const gateId of gates) {
    for (const el of mount.querySelectorAll(`[data-gate-id="${gateId}"]`)) {
      el.classList.add("is-suggestion-target");
    }
  }
  // signals + outputs share the same data-signal-id namespace (inputs
  // and output cmds are distinguished by data-node-kind, but the
  // selector is identical).
  for (const signalId of [...signals, ...outputs]) {
    for (const el of mount.querySelectorAll(`[data-signal-id="${signalId}"]`)) {
      el.classList.add("is-suggestion-target");
    }
  }
  for (const summaryId of summaries) {
    for (const el of mount.querySelectorAll(`[data-summary-id="${summaryId}"]`)) {
      el.classList.add("is-suggestion-target");
    }
  }
}

// Backwards-compat alias. Keep the old name callable so any external
// page or skill that imports workbench.js (e.g. via a bookmarklet or
// the test harness) doesn't break — it just gets the gate-only subset
// of the new behavior.
function highlightSuggestionGates(gateIds) {
  highlightSuggestionNodes({ gates: gateIds || [] });
}

function clearSuggestionInterpretation() {
  _lastInterpretation = null;
  const card = document.getElementById("workbench-suggestion-interpretation");
  if (card) {
    card.hidden = true;
    card.dataset.state = "empty";
  }
  // P59-03: clear all node highlights, not just gate-only.
  highlightSuggestionNodes({});
  // P59-03: also hide the recommended work-order draft so a stale
  // ticket from a previous interpretation doesn't bleed into a
  // re-interpret / cancel cycle.
  const rec = document.getElementById("workbench-suggestion-recommendation");
  if (rec) {
    rec.hidden = true;
    rec.removeAttribute("open");
  }
  const recText = document.getElementById(
    "workbench-suggestion-recommendation-text",
  );
  if (recText) recText.textContent = "";
  const status = document.getElementById("workbench-suggestion-status");
  if (status) {
    status.dataset.status = "idle";
    status.textContent = "";
  }
  // P54-09: any conflict banner from a previous attempt should not
  // bleed across a re-interpret / cancel.
  hideConflictBanner();
}

async function submitSuggestionTicket(systemIdOverride) {
  const status = document.getElementById("workbench-suggestion-status");
  if (!_lastInterpretation) {
    if (status) {
      status.dataset.status = "error";
      status.textContent = "尚无解读结果可提交 · no interpretation to submit yet";
    }
    return;
  }
  // Codex round-4 P2-2: prefer the system_id snapshotted at confirm
  // time over the live dropdown. This protects against a system
  // toggle that happens between confirm-click and POST — without
  // it, the conflict-checked interpretation could be filed under a
  // different system's inbox.
  const identity = document.getElementById("workbench-identity");
  const ticketChip = document.getElementById("workbench-ticket");
  const systemSelect = document.getElementById("workbench-system-select");
  const liveSystemId = systemSelect ? systemSelect.value || "thrust-reverser" : "thrust-reverser";
  const systemId = systemIdOverride || liveSystemId;
  const payload = {
    source_text: _lastInterpretation.source_text || "",
    interpretation: _lastInterpretation,
    author_name: identity ? identity.getAttribute("data-identity-name") || "anonymous" : "anonymous",
    author_role: identity ? identity.getAttribute("data-role") || "ENGINEER" : "ENGINEER",
    ticket_id: ticketChip ? ticketChip.getAttribute("data-ticket") || "ad-hoc" : "ad-hoc",
    system_id: systemId,
  };
  if (status) {
    status.dataset.status = "loading";
    status.textContent = "提交中… · submitting…";
  }
  try {
    const response = await fetch(PROPOSALS_PATH, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (response.status !== 201) {
      throw new Error(`HTTP ${response.status}`);
    }
    const created = await response.json();
    const input = document.getElementById("workbench-suggestion-input");
    if (input) {
      input.value = "";
    }
    clearSuggestionInterpretation();
    if (status) {
      status.dataset.status = "success";
      status.textContent = `工单 ${created.id} 已提交 · ticket ${created.id} submitted`;
    }
    // P54-09 + Codex round-5 P2-1: clear the autosaved draft for
    // the system we actually submitted under (NOT just the live
    // dropdown, which may have been flipped after the snapshot).
    // Otherwise the just-submitted system keeps its draft and
    // resurrects it on next refresh.
    clearSuggestionDraftFor(systemId);
    await loadProposalsInbox();
  } catch (error) {
    if (status) {
      status.dataset.status = "error";
      status.textContent = `提交失败 · submit failed: ${error.message || error}`;
    }
  }
}

// ─── P54-09 (2026-04-28): pre-submit conflict warning ───────────────
//
// Before POSTing a confirmed interpretation, fetch OPEN proposals
// scoped to the same system and detect overlap on `affected_gates`.
// If any conflicting OPEN proposal exists, show the conflict-banner
// inside the interpretation card and let the engineer choose
// "继续提交" (call submitSuggestionTicket) or "取消" (close banner,
// keep the interpretation visible so they can re-interpret / cancel).
//
// The check is best-effort: any GET failure falls through to a normal
// submit so the user is never blocked by a flaky network. The check
// is also skipped entirely when affected_gates is empty (no overlap
// possible). Single API roundtrip — the inbox endpoint returns
// status-filtered records already.
async function onConfirmClicked() {
  const status = document.getElementById("workbench-suggestion-status");
  if (!_lastInterpretation) {
    if (status) {
      status.dataset.status = "error";
      status.textContent = "尚无解读结果可提交 · no interpretation to submit yet";
    }
    return;
  }
  // Codex round-3 P2-2 + round-4 P2-2: snapshot BOTH the
  // interpretation identity and the active system_id at
  // request-start. The conflict check is async; while in flight,
  // the user could (a) hit "↻ 重新解读" and replace
  // _lastInterpretation, or (b) flip the system dropdown. Either
  // mutates the post-await state in a way that would let us file
  // a system-A interpretation under system-B's inbox after having
  // checked the wrong conflict set. We discard responses whose
  // snapshot no longer matches the live state, AND we pass the
  // snapshotted system_id into submitSuggestionTicket so the POST
  // body uses the system the engineer was actually confirming.
  const snapshot = _lastInterpretation;
  const systemSelect = document.getElementById("workbench-system-select");
  const systemId = systemSelect ? systemSelect.value || "thrust-reverser" : "thrust-reverser";
  const gates = (snapshot.affected_gates || []).slice();
  if (gates.length === 0) {
    submitSuggestionTicket(systemId);
    return;
  }
  let conflicts = [];
  try {
    const url =
      PROPOSALS_PATH +
      "?status=OPEN&system=" + encodeURIComponent(systemId);
    const resp = await fetch(url, { headers: { Accept: "application/json" } });
    if (_lastInterpretation !== snapshot) return;
    if (_currentSystemFromSelect() !== systemId) return;
    if (resp.ok) {
      const payload = await resp.json();
      if (_lastInterpretation !== snapshot) return;
      if (_currentSystemFromSelect() !== systemId) return;
      const open = (payload && payload.proposals) || [];
      conflicts = open.filter((p) => {
        const g = (p && p.interpretation && p.interpretation.affected_gates) || [];
        return Array.isArray(g) && g.some((x) => gates.includes(x));
      });
    }
  } catch (_e) {
    if (_lastInterpretation !== snapshot) return;
    if (_currentSystemFromSelect() !== systemId) return;
    conflicts = [];
  }
  if (conflicts.length === 0) {
    submitSuggestionTicket(systemId);
    return;
  }
  // Hand the snapshotted system_id to the proceed button so a
  // post-banner click still files under the correct system even if
  // the user has since flipped the dropdown.
  showConflictBanner(conflicts, gates, systemId);
}

function _currentSystemFromSelect() {
  const sel = document.getElementById("workbench-system-select");
  return (sel && sel.value) || "thrust-reverser";
}

function showConflictBanner(conflicts, currentGates, systemSnapshot) {
  const banner = document.getElementById("workbench-suggestion-conflict-banner");
  const countEl = document.getElementById("workbench-suggestion-conflict-count");
  const gatesEl = document.getElementById("workbench-suggestion-conflict-gates");
  const list = document.getElementById("workbench-suggestion-conflict-list");
  if (!banner || !list) return;
  // Stash the system_id this banner was rendered with — proceed
  // must file under the same system, even if the user toggles the
  // dropdown while looking at the warning (Codex round-4 P2-2).
  if (systemSnapshot) {
    banner.setAttribute("data-system-snapshot", systemSnapshot);
  } else {
    banner.removeAttribute("data-system-snapshot");
  }
  if (countEl) countEl.textContent = String(conflicts.length);
  if (gatesEl) gatesEl.textContent = (currentGates || []).join(", ");
  // Build the conflict list — short id, summary preview, gate pills.
  list.innerHTML = "";
  for (const p of conflicts.slice(0, 5)) {
    const li = document.createElement("li");
    const id = (p && p.id) || "PROP-?";
    const interp = (p && p.interpretation) || {};
    const summary =
      interp.summary_zh ||
      interp.summary_en ||
      (p && p.source_text) ||
      "(no summary)";
    const gates = (interp.affected_gates || []).join(", ");
    li.innerHTML =
      `<span class="conflict-id">${escapeHtml(id.slice(0, 24))}</span>` +
      `<span class="conflict-summary" title="${escapeHtml(summary)}">${escapeHtml(summary)}</span>` +
      `<span class="conflict-gates">${escapeHtml(gates)}</span>`;
    list.appendChild(li);
  }
  if (conflicts.length > 5) {
    const more = document.createElement("li");
    more.className = "conflict-more";
    more.textContent = `… 以及 ${conflicts.length - 5} 个其他 OPEN 工单 · …and ${conflicts.length - 5} more OPEN proposals`;
    list.appendChild(more);
  }
  banner.hidden = false;
}

function hideConflictBanner() {
  const banner = document.getElementById("workbench-suggestion-conflict-banner");
  if (banner) banner.hidden = true;
}

// ─── P54-09 (2026-04-28): draft autosave + restore ──────────────────
//
// Persist the engineer's in-flight typing to localStorage so an
// accidental tab-close doesn't lose the suggestion. On page boot,
// if a draft < 1h old exists FOR THE CURRENTLY ACTIVE SYSTEM, surface
// a banner offering to restore. On submit success the draft is
// cleared.
//
// Codex P54-09 round-1 P2-1 fix: drafts must be scoped by system_id.
// Without this, an engineer typing on thrust-reverser, switching to
// C919, and refreshing would be offered the thrust-reverser draft —
// then submitSuggestionTicket() would file it under C919, mis-routing
// the proposal. We persist {text, ts, system_id} per-system and only
// surface the draft whose system_id matches the live select value.
//
// Storage layout: a single key holding a map {<system_id>: draft} so
// each system carries its own most-recent draft and they don't bleed.
const SUGGESTION_DRAFT_KEY = "workbench/suggestion-drafts/v2";
const SUGGESTION_DRAFT_TTL_MS = 60 * 60 * 1000;  // 1h
const SUGGESTION_DRAFT_DEBOUNCE_MS = 500;
let _suggestionDraftTimer = null;
// Codex round-6 P2: mirror of the most recent unsaved typing —
// cleared when the debounce fires (committed to localStorage) and
// flushed proactively on system change so the user's last burst of
// keystrokes isn't lost when they realize the wrong system is on
// and switch within the debounce window.
let _pendingDraftText = null;
let _pendingDraftSystemId = null;

function installSuggestionDraftRestore() {
  const input = document.getElementById("workbench-suggestion-input");
  if (!input) return;
  // Autosave on input (debounced) — scoped to the active system.
  // Codex round-2 P2-1: capture both the system_id AND the text at
  // the moment of typing, NOT inside the timer callback. Without
  // this snapshot, switching systems within the 500ms debounce
  // window would let the old text get committed under the new
  // system_id, defeating the per-system isolation this whole flow
  // is built around.
  input.addEventListener("input", () => {
    // Codex round-4 P3: once the user starts typing, the restore
    // banner becomes stale — its preview/age refers to a draft
    // they're now overwriting. Pressing 恢复 would clobber the
    // fresh typing; pressing 忽略 would delete the just-saved
    // autosave instead of the original draft. Hide the banner the
    // moment the input becomes dirty.
    if (input.value && input.value.length > 0) {
      hideDraftBanner();
    }
    const sysSnapshot = _currentDraftSystemId();
    const textSnapshot = input.value;
    // Codex round-6 P2: track the most recent typed snapshot so
    // the system-change handler can flush it under the OLD system
    // before canceling the debounce — otherwise mid-debounce
    // switches lose the user's last 0–500ms of typing entirely.
    _pendingDraftText = textSnapshot;
    _pendingDraftSystemId = sysSnapshot;
    if (_suggestionDraftTimer) clearTimeout(_suggestionDraftTimer);
    _suggestionDraftTimer = setTimeout(
      () => {
        saveSuggestionDraftFor(sysSnapshot, textSnapshot);
        // Pending mirror is now committed — clear so a later
        // system switch doesn't double-flush.
        _pendingDraftText = null;
        _pendingDraftSystemId = null;
      },
      SUGGESTION_DRAFT_DEBOUNCE_MS,
    );
  });
  // On boot, surface a restore banner if a fresh draft exists for
  // the currently active system. Switching systems should clear the
  // banner (the new system might have its own draft, or none).
  const draft = readSuggestionDraft();
  if (draft && (input.value || "").trim() === "") {
    showDraftBanner(draft);
  }
  // When the system changes, re-evaluate which (if any) draft is
  // applicable, and cancel any pending debounce so old text doesn't
  // leak into the new system's slot (Codex round-2 P2-1).
  const systemSelect = document.getElementById("workbench-system-select");
  if (systemSelect) {
    systemSelect.addEventListener("change", () => {
      // Codex round-6 P2: flush any pending unsaved edit under the
      // OLD system before we kill the debounce — otherwise typing
      // → switching within 500ms silently discards the last burst,
      // exactly the case the restore banner is supposed to protect.
      if (_pendingDraftText !== null && _pendingDraftSystemId) {
        saveSuggestionDraftFor(_pendingDraftSystemId, _pendingDraftText);
        _pendingDraftText = null;
        _pendingDraftSystemId = null;
      }
      if (_suggestionDraftTimer) {
        clearTimeout(_suggestionDraftTimer);
        _suggestionDraftTimer = null;
      }
      hideDraftBanner();
      // Codex round-5 P2-1 (broader fix): dismiss any pending
      // conflict banner too. Otherwise a user who started a
      // confirm flow under system A, switched to system B, and
      // clicked 继续提交 would file under A while currently
      // viewing B — and post-submit cleanup state would split
      // across two systems. By killing the banner on switch we
      // simply force re-interpretation under the new system.
      hideConflictBanner();
      // Codex round-9 P2-2 + round-10 P1: the textarea + banners
      // get reset to reflect the new system, AND the in-flight
      // interpretation must be torn down too. Otherwise after a
      // switch the UI looks "reset" but _lastInterpretation still
      // holds the old gate set, and a stray Confirm click would
      // submit those old gates under the NEW system_id, mis-routing
      // proposals across system inboxes. Use the existing
      // clearSuggestionInterpretation helper so the SVG highlight
      // + status row + interpretation card all clear together.
      clearSuggestionInterpretation();
      input.value = "";
      const next = readSuggestionDraft();
      if (next) showDraftBanner(next);
    });
  }
  // Wire the banner's restore + dismiss buttons.
  const restoreBtn = document.getElementById("workbench-suggestion-draft-restore");
  const dismissBtn = document.getElementById("workbench-suggestion-draft-dismiss");
  if (restoreBtn) {
    restoreBtn.addEventListener("click", () => {
      const cur = readSuggestionDraft();
      if (cur && cur.text) {
        input.value = cur.text;
        input.focus();
      }
      hideDraftBanner();
    });
  }
  if (dismissBtn) {
    dismissBtn.addEventListener("click", () => {
      clearSuggestionDraft();
      hideDraftBanner();
    });
  }
}

function _currentDraftSystemId() {
  const sel = document.getElementById("workbench-system-select");
  return (sel && sel.value) || "thrust-reverser";
}

function _readDraftMap() {
  try {
    const raw = window.localStorage.getItem(SUGGESTION_DRAFT_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : {};
  } catch (_e) {
    return {};
  }
}

function _writeDraftMap(map) {
  try {
    window.localStorage.setItem(SUGGESTION_DRAFT_KEY, JSON.stringify(map));
  } catch (_e) { /* quota/disabled — silent */ }
}

function readSuggestionDraft() {
  const sysId = _currentDraftSystemId();
  const map = _readDraftMap();
  const draft = map[sysId];
  if (!draft || typeof draft.text !== "string" || !draft.text.trim()) return null;
  const ts = typeof draft.ts === "number" ? draft.ts : 0;
  if (Date.now() - ts > SUGGESTION_DRAFT_TTL_MS) {
    delete map[sysId];
    _writeDraftMap(map);
    return null;
  }
  // Echo system_id so the banner / submit path can sanity-check.
  return { text: draft.text, ts: ts, system_id: sysId };
}

function saveSuggestionDraft(text) {
  saveSuggestionDraftFor(_currentDraftSystemId(), text);
}

// Codex round-2 P2-1: explicit-system variant so the debounce
// callback can write under the system_id captured when the user
// was actually typing — protecting against the typing-then-switching
// race within the 500ms debounce window.
function saveSuggestionDraftFor(sysId, text) {
  if (!sysId) return;
  const map = _readDraftMap();
  if (!text || !text.trim()) {
    delete map[sysId];
  } else {
    map[sysId] = { text: text, ts: Date.now(), system_id: sysId };
  }
  _writeDraftMap(map);
}

function clearSuggestionDraft() {
  clearSuggestionDraftFor(_currentDraftSystemId());
}

// Codex round-5 P2-1: explicit-system clear so the post-submit
// cleanup wipes the draft for the system we actually filed under,
// not whatever the live dropdown points at. Without this, a
// cross-system submit (snapshot != live) would leave the submit-
// system's draft alive and reappear on next refresh.
function clearSuggestionDraftFor(sysId) {
  // Codex round-7 P2 + round-8 P3: also clear the pending-snapshot
  // mirror if (and only if) it belongs to the system being cleared.
  // The simpler "always null" version dropped another system's
  // in-flight typing in the cross-system flow:
  //   submit-A in flight → user switches to B + types → submit-A
  //   resolves and runs clearSuggestionDraftFor("A"), but that
  //   nulled the pending snapshot for B, so B's keystrokes never
  //   reached localStorage. Scoped clear preserves B's autosave.
  if (_pendingDraftSystemId === sysId) {
    _pendingDraftText = null;
    _pendingDraftSystemId = null;
    // Same scoping for the debounce timer: only kill it if it was
    // scheduled for the system we're clearing (i.e. the same
    // system as the now-cleared pending snapshot). Otherwise we
    // might cancel a debounce that was about to commit some other
    // system's typing.
    if (_suggestionDraftTimer) {
      clearTimeout(_suggestionDraftTimer);
      _suggestionDraftTimer = null;
    }
  }
  if (!sysId) return;
  const map = _readDraftMap();
  if (sysId in map) {
    delete map[sysId];
    _writeDraftMap(map);
  }
}

function showDraftBanner(draft) {
  const banner = document.getElementById("workbench-suggestion-draft-banner");
  if (!banner) return;
  const ageMin = Math.max(1, Math.round((Date.now() - draft.ts) / 60000));
  const ageEl = document.getElementById("workbench-suggestion-draft-age");
  if (ageEl) ageEl.textContent = String(ageMin);
  for (const mirror of banner.querySelectorAll('[data-mirror="age"]')) {
    mirror.textContent = String(ageMin);
  }
  const preview = document.getElementById("workbench-suggestion-draft-preview");
  if (preview) {
    const trimmed = (draft.text || "").trim();
    preview.textContent = trimmed.length > 60 ? `"${trimmed.slice(0, 60)}…"` : `"${trimmed}"`;
  }
  banner.hidden = false;
}

function hideDraftBanner() {
  const banner = document.getElementById("workbench-suggestion-draft-banner");
  if (banner) banner.hidden = true;
}

// ─────────────────────────────────────────────────────────────────
// P44-03 (2026-04-26): proposal inbox.
// P44-04 (2026-04-26): _latestProposals doubles as the source of
// truth for the review-mode glowing-anchor overlay below.
// ─────────────────────────────────────────────────────────────────

const PROPOSALS_PATH = "/api/proposals";

let _latestProposals = [];

// P55-02 round-4 (2026-04-28): freshness flag for the always-on
// marker layer. Markers paint only when this is true (i.e. we have
// a successfully-fetched proposal set). loadProposalsInbox() flips
// it to false the moment a refresh starts and the moment a fetch
// fails, so any subsequent `applyReviewAnchors(_latestProposals)`
// (e.g. from setReviewMode or circuit re-hydration) tears down
// rather than repaints from stale data. _latestProposals itself
// stays preserved so the panel-version chip's accepted count and
// click-target resolution don't lie about approval history.
let _proposalsAreFresh = false;

function installProposalInbox() {
  const refreshBtn = document.getElementById("annotation-inbox-refresh-btn");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => loadProposalsInbox());
  }
  // Fire-and-forget initial load — runs in parallel with circuit hero
  // hydration so the inbox shows up as soon as the proposals API
  // responds, regardless of how long the SVG fetch takes.
  loadProposalsInbox();
  // P48-06: poll for pending skill executions so approve cards
  // auto-appear (CLI starts an exec → workbench picks it up
  // within 5s) and auto-clear (CLI consumes signal → exec leaves
  // ASKING → next poll renders empty).
  startPendingExecPoll(5000);
  // P50-02a: also fire an immediate metrics fetch so the panel
  // is populated before the first 5s tick.
  refreshExecutionMetrics();
}

async function loadProposalsInbox() {
  const list = document.getElementById("annotation-inbox-list");
  if (!list) {
    return;
  }
  list.dataset.inboxState = "loading";
  // Codex P55-02 round-4 P3: tear down stale markers the moment a
  // refresh starts. Otherwise the always-on layer keeps advertising
  // the previous OPEN-ticket counts during the loading window — and
  // those counts could already be wrong (another reviewer could
  // have flipped a status). The pre-P55-02 review-mode-only badges
  // didn't leak stale state because they were behind a toggle.
  _proposalsAreFresh = false;
  applyReviewAnchors([]);
  // P45-02 (2026-04-26): scope the inbox to the currently-selected
  // system. The dropdown is the single source of truth (same one
  // that drives the circuit fragment in P45-01); a tile in the
  // inbox header echoes the scope so the engineer can tell which
  // system they're looking at.
  const system = currentWorkbenchSystem();
  list.dataset.inboxSystem = system;
  refreshInboxHeaderForSystem(system);
  try {
    const response = await fetch(`${PROPOSALS_PATH}?system=${encodeURIComponent(system)}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const body = await response.json();
    const proposals = Array.isArray(body.proposals) ? body.proposals : [];
    _latestProposals = proposals;
    // Codex P55-02 round-4: mark fresh BEFORE applyReviewAnchors so
    // the freshness gate lets the marker repaint go through.
    _proposalsAreFresh = true;
    renderProposalsInbox(proposals);
    list.dataset.inboxState = proposals.length === 0 ? "empty" : "ready";
    // P44-04: refresh the review-mode anchors against the new
    // proposal set. Safe no-op if review mode is off — the CSS rule
    // gated on body[data-review-mode="off"] hides every anchor.
    applyReviewAnchors(proposals);
    // P44-06: refresh the panel-version chip's accepted-count.
    refreshPanelVersionChip();
  } catch (error) {
    list.dataset.inboxState = "error";
    list.innerHTML =
      `<li class="workbench-annotation-inbox-empty">` +
      `载入工单列表失败 · failed to load proposals: ${error.message || error}` +
      `</li>`;
    // Codex P55-02 round-2 P2: gate markers are now always-on, so a
    // refresh failure must clear the marker DOM too — otherwise the
    // canvas keeps showing the previous render's counts while the
    // inbox correctly switches to the error state.
    //
    // Codex P55-02 round-3 P2: leave _latestProposals + the panel-
    // version chip alone. Resetting _latestProposals would zero the
    // chip's accepted count even though no approval state actually
    // changed — a fresh transient outage shouldn't lie about
    // approval history. The inbox surface already signals the
    // failure ("failed to load proposals") and the marker DOM is
    // gone, so there's nothing left to interact with on stale data
    // until the next successful refresh repaints both layers.
    //
    // Codex P55-02 round-5 P2: re-assert _proposalsAreFresh = false
    // here. Overlapping refreshes (system switch while a prior load
    // is in flight) can let an older success flip the flag back to
    // true before this later request's catch fires. Without this
    // line, a subsequent setReviewMode() or circuit re-hydration
    // would resurrect markers from stale data.
    _proposalsAreFresh = false;
    applyReviewAnchors([]);
  }
}

function renderProposalsInbox(proposals) {
  const list = document.getElementById("annotation-inbox-list");
  if (!list) {
    return;
  }
  if (proposals.length === 0) {
    list.innerHTML =
      `<li class="workbench-annotation-inbox-empty">` +
      `暂无已提交工单 · no proposals submitted yet` +
      `</li>`;
    return;
  }
  const escape = (text) =>
    String(text == null ? "" : text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  const items = proposals
    .map((p) => {
      const interp = p.interpretation || {};
      const gates = (interp.affected_gates || []).join(", ") || "—";
      const targets = (interp.target_signals || []).join(", ") || "—";
      const summary = interp.summary_zh || interp.summary_en || "(无 · empty)";
      const author = p.author_name || "anonymous";
      // P44-05: accept/reject buttons. Only OPEN proposals get them
      // (terminal proposals just show the status pill); CSS gates
      // visibility on body[data-review-mode="on"] so engineers don't
      // see actionable buttons on tickets they merely submitted.
      const actions = p.status === "OPEN"
        ? (
            `<div class="workbench-annotation-inbox-item-actions">` +
            `  <button type="button" class="workbench-toolbar-button is-primary" ` +
            `          data-proposal-action="accept" data-proposal-id="${escape(p.id)}">` +
            `    ✅ 通过 · Accept</button>` +
            `  <button type="button" class="workbench-toolbar-button" ` +
            `          data-proposal-action="reject" data-proposal-id="${escape(p.id)}">` +
            `    ✕ 驳回 · Reject</button>` +
            `</div>`
          )
        : "";
      // P44-06: rollback hints. Only ACCEPTED proposals get them —
      // they're the ones that have (or will have) a corresponding
      // truth-engine commit the engineer might want to revert. The
      // hints are pure read-only instructions; the workbench never
      // executes git mutations.
      const rollback = p.status === "ACCEPTED"
        ? (
            `<button type="button" class="workbench-rollback-toggle" ` +
            `        data-rollback-toggle-for="${escape(p.id)}" aria-expanded="false">` +
            `  🔁 回滚指引 · Rollback hints</button>` +
            `<div class="workbench-rollback-hints" ` +
            `     data-rollback-hints-for="${escape(p.id)}" data-rollback-state="closed">` +
            renderRollbackHints(p) +
            `</div>`
          )
        : "";
      // P47-02 (2026-04-27): kind badge + revert affordances.
      // - kind="revert" → render a banner showing the original PROP id
      //   and the truth-engine SHA being reverted, plus a "modify" tag
      //   on modify proposals stays implicit.
      // - kind="modify" + ACCEPTED + landed_truth_sha → render a
      //   "提议回退此修改" button that creates a new revert proposal
      //   via POST /api/proposals/<id>/propose-revert. The button is
      //   hidden if there's no landed sha yet (the executor hasn't
      //   recorded the merge SHA).
      const kind = p.kind || "modify";
      const kindBadge = kind === "revert"
        ? (
            `<span class="workbench-annotation-inbox-item-kind-badge" ` +
            `      data-proposal-kind="revert">🔄 REVERT</span>`
          )
        : "";
      const revertBanner = kind === "revert"
        ? (
            `<div class="workbench-annotation-inbox-item-revert-banner" ` +
            `     data-revert-of="${escape(p.revert_of_proposal_id || "")}">` +
            `  ↩ 回退目标 · Reverts: ` +
            `<code>${escape(p.revert_of_proposal_id || "—")}</code>` +
            ` · commit <code>${escape(p.revert_target_sha || "—")}</code>` +
            `</div>`
          )
        : "";
      const proposeRevertBtn =
        kind === "modify" && p.status === "ACCEPTED" && p.landed_truth_sha
          ? (
              `<button type="button" class="workbench-toolbar-button workbench-propose-revert-button" ` +
              `        data-propose-revert-for="${escape(p.id)}" ` +
              `        title="为这条已落地的修改创建一张回退工单。回退也走完整工单闭环（提议→评审→执行）。 · ` +
              `Create a revert ticket for this landed change. Reverts go through the full proposal flow.">` +
              `  ↩ 提议回退此修改 · Propose revert</button>`
            )
          : "";
      const landedSha = p.landed_truth_sha
        ? (
            `<span class="workbench-annotation-inbox-item-landed">已落地 · landed: ` +
            `<code>${escape(p.landed_truth_sha)}</code></span>`
          )
        : "";
      // P48-06 (2026-04-27): pending-execution slot. Filled
      // asynchronously by refreshPendingExecutions() — empty
      // until that fetch resolves.
      const pendingSlot =
        `<div class="workbench-pending-exec-slot" ` +
        `     data-pending-exec-for="${escape(p.id)}"></div>`;
      // P49-01b (2026-04-27): execution-state badge slot. Filled
      // asynchronously by refreshExecutionBadges() with one of 9
      // possible states (INIT/PLANNING/ASKING/EDITING/TESTING/
      // PR_OPEN/LANDED/ABORTED/FAILED). Empty until that fetch
      // resolves; absent entirely if no audit exists for this
      // proposal yet.
      const execBadgeSlot =
        `<span class="workbench-execution-badge-slot" ` +
        `      data-execution-badge-for="${escape(p.id)}"></span>`;
      return (
        `<li class="workbench-annotation-inbox-item" data-proposal-id="${escape(p.id)}" data-status="${escape(p.status)}" data-proposal-kind="${escape(kind)}">` +
        `  <div class="workbench-annotation-inbox-item-line">` +
        `    <span class="workbench-annotation-inbox-item-id">${escape(p.id)}</span>` +
        `    <span class="workbench-annotation-inbox-item-status" data-status="${escape(p.status)}">${escape(p.status)}</span>` +
        kindBadge +
        execBadgeSlot +
        `    <span class="workbench-annotation-inbox-item-gate">命中 · gate: ${escape(gates)}</span>` +
        `    <span class="workbench-annotation-inbox-item-kind">${escape(interp.change_kind_zh || "")} · ${escape(interp.change_kind_en || "")}</span>` +
        `  </div>` +
        `  <div class="workbench-annotation-inbox-item-meta">` +
        `    <span>${escape(author)}</span> · ` +
        `    <span>${escape(p.created_at || "")}</span> · ` +
        `    <span>signals: ${escape(targets)}</span>` +
        (landedSha ? ` · ${landedSha}` : "") +
        `  </div>` +
        revertBanner +
        `  <div class="workbench-annotation-inbox-item-summary">${escape(summary)}</div>` +
        pendingSlot +
        actions +
        proposeRevertBtn +
        rollback +
        `</li>`
      );
    })
    .join("");
  list.innerHTML = items;
  // P48-06: kick off pending-execution refresh now that the cards
  // exist. The refresher renders into each card's pendingSlot.
  refreshPendingExecutions();
  // P49-01b: render 9-state execution badge per card.
  refreshExecutionBadges();
  // P44-04: clicking a ticket card spotlights its anchor on the SVG.
  // Delegated handler — re-attached on every render so it always
  // matches the current set of cards.
  for (const card of list.querySelectorAll(".workbench-annotation-inbox-item")) {
    card.addEventListener("click", (event) => {
      // Ignore clicks on action buttons — they have their own
      // dedicated handlers below and shouldn't double-fire as a
      // gate-spotlight.
      if (event.target.closest("[data-proposal-action]")) return;
      const id = card.getAttribute("data-proposal-id");
      const proposal = (_latestProposals || []).find((p) => p.id === id);
      const gates = (proposal && proposal.interpretation && proposal.interpretation.affected_gates) || [];
      for (const gateId of gates) {
        spotlightCircuitGate(gateId);
      }
    });
  }
  // P44-05: accept/reject buttons. Delegated handler — re-attached
  // every render alongside the cards.
  for (const btn of list.querySelectorAll("[data-proposal-action]")) {
    btn.addEventListener("click", (event) => {
      event.stopPropagation();  // don't trigger the card click
      const action = btn.getAttribute("data-proposal-action");
      const id = btn.getAttribute("data-proposal-id");
      transitionProposal(id, action);
    });
  }
  // P44-06: rollback-hints expander toggle. Same delegated pattern.
  for (const btn of list.querySelectorAll("[data-rollback-toggle-for]")) {
    btn.addEventListener("click", (event) => {
      event.stopPropagation();
      const id = btn.getAttribute("data-rollback-toggle-for");
      const hints = list.querySelector(`[data-rollback-hints-for="${id}"]`);
      if (!hints) return;
      const open = hints.getAttribute("data-rollback-state") === "open";
      hints.setAttribute("data-rollback-state", open ? "closed" : "open");
      btn.setAttribute("aria-expanded", open ? "false" : "true");
    });
  }
  // P47-02 (2026-04-27): propose-revert button. Creates a new revert
  // proposal targeting the landed truth-engine commit; on success,
  // refreshes the inbox so the new revert ticket appears at the top.
  for (const btn of list.querySelectorAll("[data-propose-revert-for]")) {
    btn.addEventListener("click", async (event) => {
      event.stopPropagation();
      const id = btn.getAttribute("data-propose-revert-for");
      if (!id) return;
      const original = (_latestProposals || []).find((p) => p.id === id);
      const sha = (original && original.landed_truth_sha) || "—";
      const ok = window.confirm(
        `为已落地工单 ${id}\n` +
        `创建一张回退工单（目标真值提交 ${sha}）？\n\n` +
        `回退也走完整工单闭环：` +
        `这只是提议，需要走 评审-接纳-执行 才会真的回退到代码上。`
      );
      if (!ok) return;
      btn.setAttribute("disabled", "");
      btn.textContent = "提交中… · submitting…";
      try {
        await proposeRevertProposal(id);
      } finally {
        btn.removeAttribute("disabled");
      }
    });
  }
}

async function proposeRevertProposal(originalProposalId) {
  try {
    const response = await fetch(
      `/api/proposals/${encodeURIComponent(originalProposalId)}/propose-revert`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      }
    );
    if (!response.ok) {
      const errBody = await response.json().catch(() => ({}));
      const detail = errBody.error || `HTTP ${response.status}`;
      window.alert(
        `创建回退工单失败 · failed to create revert proposal:\n${detail}`
      );
      return;
    }
    await loadProposalsInbox();
  } catch (e) {
    window.alert(
      `创建回退工单出错 · network error:\n${(e && e.message) || e}`
    );
  }
}

// ─────────────────────────────────────────────────────────────────
// P48-06 (2026-04-27): pending-execution approval bridge.
//
// When a proposal has a skill-execution audit in ASKING state,
// the inbox card shows an "approval card" inside its pendingSlot
// with the plan rationale + edits + Approve/Reject buttons.
// Clicking Approve POSTs to /api/skill-executions/<id>/approve;
// the demo_server writes a signal file the CLI executor's polling
// callback consumes.
//
// We refresh pending executions after every loadProposalsInbox()
// AND on a 5s timer so the UI auto-clears once the CLI consumes
// the signal and transitions out of ASKING.
// ─────────────────────────────────────────────────────────────────

const SKILL_EXECUTIONS_PENDING_PATH = "/api/skill-executions/pending";
let _pendingExecPollHandle = null;

async function refreshPendingExecutions() {
  const slots = document.querySelectorAll("[data-pending-exec-for]");
  if (!slots.length) return;
  let executions = [];
  try {
    const r = await fetch(SKILL_EXECUTIONS_PENDING_PATH);
    if (!r.ok) return;
    const body = await r.json();
    executions = body.executions || [];
  } catch (_) {
    return;
  }
  // Index by proposal_id for O(1) lookup
  const byProposal = {};
  for (const exec of executions) {
    byProposal[exec.proposal_id] = exec;
  }
  for (const slot of slots) {
    const proposalId = slot.getAttribute("data-pending-exec-for");
    const exec = byProposal[proposalId];
    if (!exec) {
      slot.innerHTML = "";
      continue;
    }
    slot.innerHTML = renderPendingExecCard(exec);
  }
  // Wire approve/reject buttons after render
  for (const btn of document.querySelectorAll("[data-pending-exec-action]")) {
    btn.addEventListener("click", async (event) => {
      event.stopPropagation();
      const action = btn.getAttribute("data-pending-exec-action");
      const execId = btn.getAttribute("data-pending-exec-id");
      btn.setAttribute("disabled", "");
      btn.textContent = action === "approve"
        ? "已批准 · sending…"
        : "已拒绝 · sending…";
      await sendPendingExecApproval(execId, action);
      // Re-poll immediately so the card reflects the new state
      refreshPendingExecutions();
    });
  }
}

function renderPendingExecCard(exec) {
  const escape = (text) =>
    String(text == null ? "" : text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  const plan = exec.plan || {};
  const rationale = plan.rationale || "";
  const namespaces = (plan.affected_namespaces || []).join(", ") || "—";
  const edits = plan.file_edits || [];
  const editsList = edits
    .slice(0, 8)
    .map(
      (e) =>
        `<li><code>${escape(e.path)}</code>` +
        (e.reason ? ` — ${escape(e.reason)}` : "") +
        `</li>`
    )
    .join("");
  const moreEdits =
    edits.length > 8 ? `<li>(and ${edits.length - 8} more)</li>` : "";
  const execId = escape(exec.exec_id);
  return (
    `<div class="workbench-pending-exec-card" data-pending-exec="true">` +
    `  <div class="workbench-pending-exec-header">` +
    `    ⏳ <strong>Plan 待审 · Awaiting plan approval</strong>` +
    `    <span class="workbench-pending-exec-id">${execId}</span>` +
    `  </div>` +
    `  <div class="workbench-pending-exec-rationale">` +
    `    <strong>Plan 说明:</strong> ${escape(rationale)}` +
    `  </div>` +
    `  <div class="workbench-pending-exec-meta">` +
    `    <span>命名空间 · namespaces: ${escape(namespaces)}</span>` +
    `  </div>` +
    `  <div class="workbench-pending-exec-edits">` +
    `    <strong>预计改动文件:</strong>` +
    `    <ul>${editsList}${moreEdits}</ul>` +
    `  </div>` +
    `  <div class="workbench-pending-exec-actions">` +
    `    <button type="button" class="workbench-toolbar-button is-primary" ` +
    `            data-pending-exec-action="approve" data-pending-exec-id="${execId}">` +
    `      ✅ 批准 · Approve</button>` +
    `    <button type="button" class="workbench-toolbar-button" ` +
    `            data-pending-exec-action="reject" data-pending-exec-id="${execId}">` +
    `      ✕ 拒绝 · Reject</button>` +
    `  </div>` +
    `</div>`
  );
}

async function sendPendingExecApproval(execId, action) {
  try {
    const r = await fetch(
      `/api/skill-executions/${encodeURIComponent(execId)}/${action}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      }
    );
    if (!r.ok) {
      const body = await r.json().catch(() => ({}));
      window.alert(
        `${action === "approve" ? "批准" : "拒绝"}失败:\n` +
        (body.error || `HTTP ${r.status}`)
      );
    }
  } catch (e) {
    window.alert(
      `${action === "approve" ? "批准" : "拒绝"}出错:\n` +
      ((e && e.message) || e)
    );
  }
}

function startPendingExecPoll(intervalMs) {
  if (_pendingExecPollHandle) return;
  // Periodic refresh so cards auto-clear once CLI consumes signal
  // AND the per-card execution-state badge stays current as the
  // executor walks through its lifecycle (P49-01b).
  // P50-02a: same loop also refreshes the metrics panel so the
  // dashboard stays current without a separate timer.
  _pendingExecPollHandle = setInterval(
    () => {
      refreshPendingExecutions();
      refreshExecutionBadges();
      refreshExecutionMetrics();
    },
    intervalMs || 5000
  );
}

// ─────────────────────────────────────────────────────────────────
// P49-01b (2026-04-27): per-proposal execution-state badge.
//
// Each accepted proposal card carries a small badge showing the
// current state of the latest skill_executor execution, drawn from
// the 9-state machine:
//
//   INIT      ◯  pre-flight, no work yet
//   PLANNING  🧠  LLM building the plan
//   ASKING    ⏳  waiting on engineer in workbench
//   EDITING   ✏  applying file edits
//   TESTING   🧪  pytest running
//   PR_OPEN   🔀  PR submitted, awaiting CI/merge
//   LANDED    ✅  merged to main
//   ABORTED   ⊘   user rejected or test gate blocked
//   FAILED    ✗   executor crashed / unrecoverable error
//
// One bulk fetch of /api/skill-executions then group by
// proposal_id (newest-first ordering preserved by list_audits).
// Cards without any audit get an empty slot — the badge appears
// only AFTER the executor has touched the proposal.
// ─────────────────────────────────────────────────────────────────

const SKILL_EXECUTIONS_PATH = "/api/skill-executions";

const EXECUTION_STATE_INFO = {
  INIT:     { glyph: "◯",  label_zh: "待启动",   label_en: "Init",     css: "init"     },
  PLANNING: { glyph: "🧠", label_zh: "计划中",   label_en: "Planning", css: "planning" },
  ASKING:   { glyph: "⏳", label_zh: "待批准",   label_en: "Asking",   css: "asking"   },
  EDITING:  { glyph: "✏",  label_zh: "改文件",   label_en: "Editing",  css: "editing"  },
  TESTING:  { glyph: "🧪", label_zh: "跑测试",   label_en: "Testing",  css: "testing"  },
  PR_OPEN:  { glyph: "🔀", label_zh: "PR待合",   label_en: "PR Open",  css: "pr-open"  },
  LANDED:   { glyph: "✅", label_zh: "已落地",   label_en: "Landed",   css: "landed"   },
  ABORTED:  { glyph: "⊘",  label_zh: "已终止",   label_en: "Aborted",  css: "aborted"  },
  FAILED:   { glyph: "✗",  label_zh: "失败",     label_en: "Failed",   css: "failed"   },
};

// P49-01c: states where Cancel is meaningful. ASKING is excluded
// because the pending-exec card already has Approve/Reject.
// Terminal states (LANDED/ABORTED/FAILED) get no Cancel button —
// nothing to cancel anymore.
const CANCELLABLE_STATES = new Set([
  "PLANNING", "EDITING", "TESTING", "PR_OPEN",
]);

function renderExecutionBadge(audit) {
  const escape = (text) =>
    String(text == null ? "" : text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  const info = EXECUTION_STATE_INFO[audit.state] || {
    glyph: "?", label_zh: audit.state, label_en: audit.state, css: "unknown",
  };
  const isBackfill = audit.audit_source === "backfill";
  const titleParts = [
    `Exec: ${audit.exec_id}`,
    `State: ${audit.state}`,
  ];
  if (isBackfill) titleParts.push("audit_source=backfill (reconstructed)");
  const cancelButton = CANCELLABLE_STATES.has(audit.state)
    ? (
        `<button type="button" class="workbench-execution-cancel-button" ` +
        `        data-execution-cancel-id="${escape(audit.exec_id)}" ` +
        `        data-execution-cancel-state="${escape(audit.state)}" ` +
        `        title="中断此次执行 · Cancel this execution">` +
        `  ✕</button>`
      )
    : "";
  return (
    `<span class="workbench-execution-badge" ` +
    `      data-execution-state="${escape(audit.state)}" ` +
    `      data-execution-css="${escape(info.css)}" ` +
    `      title="${escape(titleParts.join(" · "))}">` +
    `  <span class="workbench-execution-badge-glyph">${escape(info.glyph)}</span>` +
    `  <span class="workbench-execution-badge-label">` +
    `    ${escape(info.label_zh)} · ${escape(info.label_en)}` +
    `  </span>` +
    (isBackfill
      ? `<span class="workbench-execution-badge-backfill" ` +
        `      title="此审计是事后回填，并非首次实时记录">↺</span>`
      : "") +
    cancelButton +
    `</span>`
  );
}

async function refreshExecutionBadges() {
  const slots = document.querySelectorAll("[data-execution-badge-for]");
  if (!slots.length) return;
  let executions = [];
  try {
    const r = await fetch(SKILL_EXECUTIONS_PATH);
    if (!r.ok) return;
    const body = await r.json();
    executions = body.executions || [];
  } catch (_) {
    return;
  }
  // list_audits returns newest-first, so the FIRST occurrence of
  // each proposal_id is the freshest audit for that proposal.
  const latestByProposal = {};
  for (const exec of executions) {
    if (!latestByProposal[exec.proposal_id]) {
      latestByProposal[exec.proposal_id] = exec;
    }
  }
  for (const slot of slots) {
    const proposalId = slot.getAttribute("data-execution-badge-for");
    const exec = latestByProposal[proposalId];
    if (!exec) {
      slot.innerHTML = "";
      continue;
    }
    slot.innerHTML = renderExecutionBadge(exec);
    // Stash the proposal_id so the click handler can fetch /timings
    const badge = slot.querySelector(".workbench-execution-badge");
    if (badge) {
      badge.setAttribute("data-execution-proposal-id", proposalId);
    }
  }
  // P50-02c: wire badge clicks to the timing tooltip. Click on
  // the badge (NOT on the cancel button or backfill marker) opens
  // a popover showing per-phase durations. Click anywhere else on
  // the page closes it.
  for (const badge of document.querySelectorAll(".workbench-execution-badge")) {
    badge.addEventListener("click", async (event) => {
      // Ignore clicks on the cancel button — that has its own
      // handler that aborts execution
      if (event.target.closest(".workbench-execution-cancel-button")) return;
      event.stopPropagation();
      const proposalId = badge.getAttribute("data-execution-proposal-id");
      if (!proposalId) return;
      await openTimingTooltip(badge, proposalId);
    });
  }

  // P49-01c: wire cancel buttons after render. Each click confirms,
  // POSTs, and triggers an immediate refresh so the badge transitions
  // to ABORTED without waiting for the 5s poll tick.
  for (const btn of document.querySelectorAll("[data-execution-cancel-id]")) {
    btn.addEventListener("click", async (event) => {
      event.stopPropagation();
      const execId = btn.getAttribute("data-execution-cancel-id");
      const stateName = btn.getAttribute("data-execution-cancel-state");
      const ok = window.confirm(
        `确认中断该次执行？ · Cancel this ${stateName} execution?\n\n` +
        `Exec: ${execId}\n\n` +
        `执行器会在下一个阶段边界停止并回滚已应用的改动。\n` +
        `The executor will stop at its next phase boundary and revert any applied edits.`
      );
      if (!ok) return;
      btn.setAttribute("disabled", "");
      btn.textContent = "…";
      await sendExecutionCancel(execId);
      // Trigger immediate refresh so the user sees the new state
      refreshExecutionBadges();
      refreshPendingExecutions();
    });
  }
}

async function sendExecutionCancel(execId) {
  try {
    const r = await fetch(
      `/api/skill-executions/${encodeURIComponent(execId)}/cancel`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      }
    );
    if (!r.ok) {
      const body = await r.json().catch(() => ({}));
      window.alert(
        `中断失败 · Cancel failed:\n` +
        (body.error || `HTTP ${r.status}`)
      );
    }
  } catch (e) {
    window.alert(
      `中断出错 · Cancel error:\n` +
      ((e && e.message) || e)
    );
  }
}

// Expose the state map + renderer for tests and console debugging.
if (typeof window !== "undefined") {
  window.__WB_EXECUTION_STATE_INFO = EXECUTION_STATE_INFO;
  window.__WB_renderExecutionBadge = renderExecutionBadge;
}


// ─────────────────────────────────────────────────────────────────
// P50-02c (2026-04-27): per-execution phase-timing tooltip.
//
// Click a badge to open a small popover that shows the time spent
// in each phase. Useful for diagnosing "why is this stuck" — a
// LANDED execution that took 30 minutes might have spent 29 in
// ASKING (engineer was slow) or in TESTING (slow test suite).
//
// The popover fetches /api/proposals/<id>/execution/timings on
// open so the data is fresh; closes on outside click.
// ─────────────────────────────────────────────────────────────────

let _activeTimingTooltip = null;

function _formatPhaseDuration(seconds) {
  if (seconds == null) return "—";
  if (seconds < 1) return "<1s";
  if (seconds < 60) return `${seconds.toFixed(0)}s`;
  if (seconds < 3600) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return s ? `${m}m${s}s` : `${m}m`;
  }
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return m ? `${h}h${m}m` : `${h}h`;
}

async function openTimingTooltip(anchor, proposalId) {
  // If a tooltip is already open, close it first
  if (_activeTimingTooltip) {
    _activeTimingTooltip.remove();
    _activeTimingTooltip = null;
  }
  let timings;
  try {
    const r = await fetch(
      `/api/proposals/${encodeURIComponent(proposalId)}/execution/timings`
    );
    if (!r.ok) return;
    if (r.status === 204) return;
    timings = await r.json();
  } catch (_) {
    return;
  }
  const tooltip = document.createElement("div");
  tooltip.className = "workbench-execution-timing-tooltip";
  tooltip.innerHTML = renderTimingTooltip(timings);
  // Position relative to anchor's bounding rect
  const rect = anchor.getBoundingClientRect();
  tooltip.style.top = `${rect.bottom + window.scrollY + 4}px`;
  tooltip.style.left = `${rect.left + window.scrollX}px`;
  document.body.appendChild(tooltip);
  _activeTimingTooltip = tooltip;

  // Close on outside click. Use capture phase so the tooltip's own
  // clicks don't propagate up and trigger close.
  const closer = (event) => {
    if (tooltip.contains(event.target)) return;
    tooltip.remove();
    _activeTimingTooltip = null;
    document.removeEventListener("click", closer, true);
  };
  // Defer attachment so the click that opened the tooltip doesn't
  // immediately close it
  setTimeout(() => {
    document.addEventListener("click", closer, true);
  }, 0);
}

function renderTimingTooltip(timings) {
  const escape = (text) =>
    String(text == null ? "" : text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  const phases = timings.timings || [];
  // Find the longest duration so we can scale bars
  const maxDur = Math.max(
    1,
    ...phases.map((p) => p.duration_sec || 0)
  );
  const rows = phases
    .map((p) => {
      const isCurrent = p.phase === timings.current_phase;
      const info = EXECUTION_STATE_INFO[p.phase] || { css: "unknown" };
      const dur = p.duration_sec;
      const widthPct = dur ? Math.max(2, (dur / maxDur) * 100) : 0;
      return (
        `<div class="workbench-timing-row${isCurrent ? " is-current" : ""}">` +
        `  <span class="workbench-timing-phase" data-execution-css="${escape(info.css)}">` +
        `    ${escape(p.phase)}` +
        `  </span>` +
        `  <div class="workbench-timing-bar-track">` +
        `    <div class="workbench-timing-bar-fill" data-execution-css="${escape(info.css)}" ` +
        `         style="width: ${widthPct.toFixed(1)}%"></div>` +
        `  </div>` +
        `  <span class="workbench-timing-duration">` +
        `    ${escape(_formatPhaseDuration(dur))}` +
        `  </span>` +
        `</div>`
      );
    })
    .join("");
  const totalLine =
    timings.total_duration_sec != null
      ? `<span class="workbench-timing-total">total ${escape(_formatPhaseDuration(timings.total_duration_sec))}</span>`
      : `<span class="workbench-timing-total">在 ${escape(timings.current_phase)} 中… · in flight</span>`;
  return (
    `<div class="workbench-timing-header">` +
    `  <strong>阶段耗时 · phase timings</strong>` +
    `  ${totalLine}` +
    `</div>` +
    `<div class="workbench-timing-rows">${rows}</div>`
  );
}

if (typeof window !== "undefined") {
  window.__WB_renderTimingTooltip = renderTimingTooltip;
  window.__WB_openTimingTooltip = openTimingTooltip;
}


// ─────────────────────────────────────────────────────────────────
// P50-02a (2026-04-27): executor observability metrics panel.
//
// Reads /api/skill-executions/metrics and renders four header
// cards (total / pass-rate / median / p95) + 9-state bar chart
// + recent-failures list. Re-runs on the same 5s poll loop as
// the badges, so reviewers see the system health update without
// page reload.
//
// Pure DOM updates — no heavy charting library. The bars are
// just <div>s with widths proportional to count/max.
// ─────────────────────────────────────────────────────────────────

const SKILL_EXECUTIONS_METRICS_PATH = "/api/skill-executions/metrics";
// P50-08b: SLO transition timeline endpoint. Pull last 20 entries
// alongside the metrics on each poll. Newest-last in the response;
// renderer reverses for a "freshest at top" display.
const SLO_HISTORY_PATH = "/api/skill-executions/slo-history?limit=20";

function _formatDuration(seconds) {
  if (seconds == null) return "—";
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
  return `${(seconds / 3600).toFixed(1)}h`;
}

function _formatPassRate(rate) {
  if (rate == null) return "—";
  return `${(rate * 100).toFixed(0)}%`;
}

// P50-10: keep the forensics-bundle link click from toggling the
// <details> panel open/closed. The link lives inside the
// <summary> so its click bubbles up to the disclosure widget by
// default; we stop propagation so the download starts without
// changing the panel's expansion state.
function _bindForensicsLink() {
  const link = document.getElementById("workbench-metrics-forensics-link");
  if (!link || link.__wbBound) return;
  link.__wbBound = true;
  link.addEventListener("click", (e) => {
    e.stopPropagation();
  });
}

// P49-02b: poll the governance-hold list on the same 5s cadence
// as the metrics panel. List endpoint: /api/skill-executions
// ?state=GOVERNANCE_HOLD. Each card surfaces verdict reasons +
// approve/reject buttons that POST to the new bridge endpoints.
const GOVERNANCE_LIST_PATH =
  "/api/skill-executions?state=GOVERNANCE_HOLD";

async function refreshGovernancePanel() {
  const panel = document.getElementById("workbench-governance-panel");
  const list = document.getElementById("workbench-governance-list");
  if (!panel || !list) return;
  let body;
  try {
    const r = await fetch(GOVERNANCE_LIST_PATH);
    if (!r.ok) return;
    body = await r.json();
  } catch (_) {
    return;
  }
  const audits = (body && body.executions) || [];
  if (audits.length === 0) {
    panel.setAttribute("hidden", "");
    list.innerHTML = "";
    return;
  }
  panel.removeAttribute("hidden");
  const escape = (text) =>
    String(text == null ? "" : text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");

  list.innerHTML = audits
    .map((rec) => {
      const review = rec.governance_review || {};
      const matches = review.matches || [];
      // Render each matched rule as its own row so the reviewer
      // sees exactly which criteria triggered the gate.
      const reasonsHtml = matches.length
        ? matches
            .map(
              (m) =>
                `<li class="workbench-governance-reason">` +
                `  <span class="workbench-governance-rule-pill" ` +
                `        data-governance-rule="${escape(m.rule_id)}">` +
                `    ${escape(m.rule_id)}` +
                `  </span>` +
                `  <span class="workbench-governance-reason-text">` +
                `    ${escape(m.reason)}` +
                `  </span>` +
                `</li>`
            )
            .join("")
        : `<li class="workbench-governance-reason workbench-governance-reason-empty">` +
          `  (no matches recorded — likely a stale audit)` +
          `</li>`;

      return (
        `<li class="workbench-governance-card" ` +
        `    data-governance-exec-id="${escape(rec.exec_id)}">` +
        `  <header class="workbench-governance-card-header">` +
        `    <span class="workbench-governance-exec-id">` +
        `      ${escape(rec.exec_id)}` +
        `    </span>` +
        `    <span class="workbench-governance-proposal-id">` +
        `      ${escape(rec.proposal_id || "")}` +
        `    </span>` +
        `  </header>` +
        `  <ul class="workbench-governance-reasons">${reasonsHtml}</ul>` +
        `  <div class="workbench-governance-actions">` +
        `    <button type="button" ` +
        `            class="workbench-governance-approve-btn" ` +
        `            data-governance-action="approve" ` +
        `            data-governance-exec-id="${escape(rec.exec_id)}">` +
        `      ✓ 批准 · approve` +
        `    </button>` +
        `    <button type="button" ` +
        `            class="workbench-governance-reject-btn" ` +
        `            data-governance-action="reject" ` +
        `            data-governance-exec-id="${escape(rec.exec_id)}">` +
        `      ✗ 拒绝 · reject` +
        `    </button>` +
        `  </div>` +
        `</li>`
      );
    })
    .join("");

  _bindGovernanceClickHandlers();
}

function _bindGovernanceClickHandlers() {
  const list = document.getElementById("workbench-governance-list");
  if (!list || list.__wbGovBound) return;
  list.__wbGovBound = true;
  // Event delegation: one handler at the list level so newly
  // rendered cards inherit it without re-binding.
  list.addEventListener("click", async (e) => {
    const target = e.target.closest("[data-governance-action]");
    if (!target) return;
    const execId = target.getAttribute("data-governance-exec-id");
    const action = target.getAttribute("data-governance-action");
    if (!execId || !action) return;
    const endpoint =
      action === "approve"
        ? `/api/skill-executions/${encodeURIComponent(execId)}/governance-approve`
        : `/api/skill-executions/${encodeURIComponent(execId)}/governance-reject`;
    target.disabled = true;
    try {
      const r = await fetch(endpoint, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          actor: "workbench-ui",
          note: "",
        }),
      });
      // Whether the response was 202 or 4xx, refresh: the next
      // poll cycle is the source of truth.
      await refreshGovernancePanel();
      if (typeof refreshExecutionMetrics === "function") {
        refreshExecutionMetrics();
      }
    } catch (_) {
      target.disabled = false;
    }
  });
}

async function refreshExecutionMetrics() {
  _bindForensicsLink();
  // P49-02b: piggyback the governance panel refresh so it runs
  // on every metrics tick. Failure here MUST NOT block the
  // metrics body — the gate panel is supplementary.
  refreshGovernancePanel().catch(() => {});
  const panel = document.getElementById("workbench-metrics-panel");
  if (!panel) return;  // page without the panel (older test harnesses)
  let metrics;
  try {
    const r = await fetch(SKILL_EXECUTIONS_METRICS_PATH);
    if (!r.ok) return;
    metrics = await r.json();
  } catch (_) {
    return;
  }
  renderExecutionMetrics(metrics);
  // P50-08b: refresh the SLO transition timeline on the same
  // poll cadence. Failures here MUST NOT block the metrics
  // panel — the timeline is supplementary.
  try {
    const h = await fetch(SLO_HISTORY_PATH);
    if (h.ok) {
      const body = await h.json();
      renderSloTimeline(body);
    }
  } catch (_) {
    // ignore
  }
  // P51-01: refresh the Plan Timeline (freshest execution's PlanStep[]).
  // Failures must not block the metrics panel — supplementary view.
  try {
    const e = await fetch(SKILL_EXECUTIONS_PATH);
    if (e.ok) {
      const body = await e.json();
      const executions = body.executions || [];
      renderPlanTimeline(executions[0] || null);
    }
  } catch (_) {
    // ignore
  }
}

function renderPlanTimeline(record) {
  const container = document.getElementById("workbench-plan-timeline");
  const title = document.getElementById("workbench-plan-timeline-title");
  const stateLabel = document.getElementById("workbench-plan-timeline-state");
  const list = document.getElementById("workbench-plan-timeline-steps");
  if (!container || !title || !list || !stateLabel) return;
  const steps = (record && record.plan_steps) || [];
  if (!record || steps.length === 0) {
    container.setAttribute("hidden", "");
    return;
  }
  container.removeAttribute("hidden");
  const escape = (text) =>
    String(text == null ? "" : text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  title.textContent = record.proposal_id || "—";
  stateLabel.textContent = record.state || "—";
  stateLabel.setAttribute("data-state", record.state || "");
  list.innerHTML = steps
    .map((s) => {
      let status = "pending";
      if (s.completed_at) status = "done";
      else if (s.started_at) status = "active";
      const est = s.estimated_seconds != null
        ? `${Math.round(s.estimated_seconds)}s`
        : "—";
      const actual = s.actual_duration_sec != null
        ? `${s.actual_duration_sec.toFixed(1)}s`
        : (status === "active" ? "运行中" : "—");
      return (
        `<li class="workbench-plan-timeline-step" data-step-status="${status}">` +
        `  <span class="workbench-plan-timeline-step-icon" aria-hidden="true">` +
        (status === "done" ? "✓" : status === "active" ? "●" : "○") +
        `  </span>` +
        `  <div class="workbench-plan-timeline-step-body">` +
        `    <strong>${escape(s.phase_name || "")}</strong>` +
        `    <span>${escape(s.description || "")}</span>` +
        `    <span class="workbench-plan-timeline-step-timing">est ${escape(est)} · actual ${escape(actual)}</span>` +
        `  </div>` +
        `</li>`
      );
    })
    .join("");
}

function renderSloTimeline(body) {
  const container = document.getElementById("workbench-metrics-slo-timeline");
  const list = document.getElementById("workbench-metrics-slo-timeline-list");
  if (!container || !list) return;
  const escape = (text) =>
    String(text == null ? "" : text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  const transitions = (body && body.transitions) || [];
  if (transitions.length === 0) {
    container.setAttribute("hidden", "");
    list.innerHTML = "";
    return;
  }
  container.removeAttribute("hidden");
  // Reverse: response is newest-last (file-order); display
  // newest-first so the freshest transition is at the top.
  const reversed = transitions.slice().reverse();
  list.innerHTML = reversed
    .map((t) => {
      const breach = (t.breach_slos || []).join(", ") || "(no breach)";
      const snap = t.snapshot || {};
      // Compact one-line summary of the snapshot at transition time.
      const passLifetime =
        snap.pass_rate != null
          ? `${(snap.pass_rate * 100).toFixed(0)}%`
          : "—";
      const passRecent =
        snap.pass_rate_recent != null
          ? `${(snap.pass_rate_recent * 100).toFixed(0)}%`
          : null;
      const recentSeg = passRecent ? ` · recent ${passRecent}` : "";
      return (
        `<li class="workbench-metrics-slo-timeline-item">` +
        `  <span class="workbench-metrics-slo-timeline-ts">` +
        `    ${escape(t.ts)}` +
        `  </span>` +
        `  <span class="workbench-metrics-slo-timeline-arrow">` +
        `    <span class="workbench-metrics-slo-pip" data-slo-severity="${escape(t.from_severity)}">` +
        `      ${escape(t.from_severity)}` +
        `    </span>` +
        `    →` +
        `    <span class="workbench-metrics-slo-pip" data-slo-severity="${escape(t.to_severity)}">` +
        `      ${escape(t.to_severity)}` +
        `    </span>` +
        `  </span>` +
        `  <span class="workbench-metrics-slo-timeline-detail">` +
        `    pass ${passLifetime}${recentSeg} · breach: ${escape(breach)}` +
        `  </span>` +
        `</li>`
      );
    })
    .join("");
}

function renderExecutionMetrics(metrics) {
  const escape = (text) =>
    String(text == null ? "" : text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");

  // Header summary line (visible even when collapsed)
  const summary = document.getElementById("workbench-metrics-summary-line");
  if (summary) {
    if (!metrics || metrics.total === 0) {
      summary.textContent = "尚无执行 · no executions yet";
    } else {
      // P50-08a: show rolling-window pass rate alongside lifetime
      // when populated. A divergence (e.g. lifetime 90%, recent 30%)
      // is visible even with the panel collapsed.
      const rw = metrics.recent_window;
      let recentSegment = "";
      if (rw && rw.pass_rate_recent != null) {
        recentSegment =
          ` · last ${rw.window_size}: ${_formatPassRate(rw.pass_rate_recent)}`;
      }
      summary.textContent =
        `${metrics.total} 次 · pass ${_formatPassRate(metrics.pass_rate)}` +
        recentSegment +
        ` · median ${_formatDuration(metrics.median_duration_sec)}`;
    }
  }

  // Header cards
  const set = (id, value) => {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  };
  set("workbench-metric-total", String(metrics.total));
  set("workbench-metric-pass-rate", _formatPassRate(metrics.pass_rate));
  set(
    "workbench-metric-median-duration",
    _formatDuration(metrics.median_duration_sec)
  );
  set(
    "workbench-metric-p95-duration",
    _formatDuration(metrics.p95_duration_sec)
  );

  // 9-state bar chart. Render every state in canonical order so
  // the layout stays stable even when some buckets are zero.
  const barsContainer = document.getElementById(
    "workbench-metrics-state-bars"
  );
  if (barsContainer && metrics.by_state) {
    const stateOrder = [
      "INIT", "PLANNING", "ASKING", "EDITING", "TESTING",
      "PR_OPEN", "LANDED", "ABORTED", "FAILED",
    ];
    const counts = stateOrder.map((s) => metrics.by_state[s] || 0);
    const maxCount = Math.max(1, ...counts);
    barsContainer.innerHTML = stateOrder
      .map((state, i) => {
        const count = counts[i];
        const info = EXECUTION_STATE_INFO[state] || { css: "unknown" };
        const widthPct = count === 0 ? 0 : Math.max(4, (count / maxCount) * 100);
        return (
          `<div class="workbench-metrics-state-row">` +
          `  <span class="workbench-metrics-state-label" data-execution-css="${escape(info.css)}">` +
          `    ${escape(state)}` +
          `  </span>` +
          `  <div class="workbench-metrics-state-bar-track">` +
          `    <div class="workbench-metrics-state-bar-fill" data-execution-css="${escape(info.css)}" ` +
          `         style="width: ${widthPct.toFixed(1)}%"></div>` +
          `  </div>` +
          `  <span class="workbench-metrics-state-count">${count}</span>` +
          `</div>`
        );
      })
      .join("");
  }

  // P50-07: SLO verdict chip + breach list. The chip lives in the
  // collapsed summary so the panel signals health at a glance; the
  // breach list expands to actionable detail when the panel opens.
  const sloChip = document.getElementById("workbench-metrics-slo-chip");
  const sloBreaches = document.getElementById(
    "workbench-metrics-slo-breaches"
  );
  const sloBreachList = document.getElementById(
    "workbench-metrics-slo-breach-list"
  );
  const slo = metrics.slo_status;
  if (sloChip) {
    const overall = (slo && slo.overall) || "no_data";
    sloChip.setAttribute("data-slo-severity", overall);
    const labels = {
      green: "🟢 GREEN",
      yellow: "🟡 YELLOW",
      red: "🔴 RED",
      no_data: "⚪ NO DATA",
    };
    sloChip.textContent = labels[overall] || "—";
  }
  if (sloBreaches && sloBreachList) {
    const breaches = (slo && slo.breaches) || [];
    if (breaches.length === 0) {
      sloBreaches.setAttribute("hidden", "");
      sloBreachList.innerHTML = "";
    } else {
      sloBreaches.removeAttribute("hidden");
      sloBreachList.innerHTML = breaches
        .map((b) => {
          return (
            `<li class="workbench-metrics-slo-breach-item" ` +
            `    data-slo-severity="${escape(b.severity)}">` +
            `  <span class="workbench-metrics-slo-breach-pill" ` +
            `        data-slo-severity="${escape(b.severity)}">` +
            `    ${escape(b.severity.toUpperCase())}` +
            `  </span>` +
            `  <span class="workbench-metrics-slo-breach-name">` +
            `    ${escape(b.slo)}` +
            `  </span>` +
            `  <span class="workbench-metrics-slo-breach-note">` +
            `    ${escape(b.note)}` +
            `  </span>` +
            `</li>`
          );
        })
        .join("");
    }
  }

  // P50-04: failure category breakdown ("what's been breaking?")
  const breakdownContainer = document.getElementById(
    "workbench-metrics-failure-breakdown"
  );
  const breakdownList = document.getElementById(
    "workbench-metrics-failure-categories"
  );
  const fc = metrics.failure_classification;
  if (breakdownContainer && breakdownList) {
    if (!fc || fc.total === 0) {
      breakdownContainer.setAttribute("hidden", "");
      breakdownList.innerHTML = "";
    } else {
      breakdownContainer.removeAttribute("hidden");
      breakdownList.innerHTML = (fc.by_category || [])
        .map((cat) => {
          const samples = (cat.sample_details || [])
            .map((s) => `<code>${escape(s)}</code>`)
            .join(", ");
          // Map backend category enum value → CSS class. Most are
          // identity (planner_error → planner_error); reuse the
          // existing aborted/failed badge palette for visual
          // continuity where applicable.
          return (
            `<li>` +
            `  <span class="workbench-metrics-failure-cat-pill" ` +
            `        data-failure-category="${escape(cat.category)}">` +
            `    ${escape(cat.category)}` +
            `  </span>` +
            `  <span class="workbench-metrics-failure-cat-count">${cat.count}</span>` +
            `  <span class="workbench-metrics-failure-cat-samples">` +
            `    ${samples || "<em>(no detail)</em>"}` +
            `  </span>` +
            `</li>`
          );
        })
        .join("");
    }
  }

  // Recent failures list
  const failuresContainer = document.getElementById(
    "workbench-metrics-failures"
  );
  if (failuresContainer) {
    const failures = metrics.recent_failures || [];
    if (failures.length === 0) {
      failuresContainer.innerHTML =
        `<p class="workbench-metrics-failures-empty">` +
        `  最近无失败 · no recent failures` +
        `</p>`;
    } else {
      failuresContainer.innerHTML =
        `<p class="workbench-metrics-failures-eyebrow">` +
        `  最近失败 · recent failures` +
        `</p>` +
        `<ul class="workbench-metrics-failures-list">` +
        failures
          .map(
            (f) =>
              `<li>` +
              `<span class="workbench-metrics-failures-state" data-execution-css="${
                f.state === "ABORTED" ? "aborted" : "failed"
              }">${escape(f.state)}</span>` +
              `<code>${escape(f.exec_id)}</code>` +
              `<span class="workbench-metrics-failures-reason">${escape(f.abort_reason)}</span>` +
              `</li>`
          )
          .join("") +
        `</ul>`;
    }
  }
}

// Expose for console debugging / future tests
if (typeof window !== "undefined") {
  window.__WB_renderExecutionMetrics = renderExecutionMetrics;
  window.__WB_refreshExecutionMetrics = refreshExecutionMetrics;
}

// ─────────────────────────────────────────────────────────────────
// P44-04 (2026-04-26): reviewer-mode glowing anchors.
//
// When the reviewer toggles "审核视角 · Review Mode" ON, each OPEN
// proposal in the inbox lights up its `interpretation.affected_gates`
// on the SVG with a pulsing glow + a small badge showing how many
// open tickets that gate has. Click a glowing anchor to scroll the
// matching ticket card into view and spotlight it; click a ticket
// card to spotlight its anchor on the SVG (handled in
// renderProposalsInbox above).
//
// Truth-engine red line: this whole module reads from /api/proposals
// only and never touches controller/runner/models/adapters.
// ─────────────────────────────────────────────────────────────────

function installReviewModeToggle() {
  const btn = document.getElementById("workbench-review-mode-toggle");
  if (!btn) {
    return;
  }
  btn.addEventListener("click", () => {
    const next = btn.getAttribute("data-review-mode-state") === "on" ? "off" : "on";
    setReviewMode(next);
  });
}

function setReviewMode(state) {
  const enabled = state === "on";
  document.body.setAttribute("data-review-mode", enabled ? "on" : "off");
  const btn = document.getElementById("workbench-review-mode-toggle");
  if (btn) {
    btn.setAttribute("data-review-mode-state", enabled ? "on" : "off");
    btn.setAttribute("aria-pressed", enabled ? "true" : "false");
    const label = btn.querySelector("[data-review-mode-label]");
    if (label) {
      label.textContent = enabled ? "开启 · On" : "关闭 · Off";
    }
  }
  applyReviewAnchors(_latestProposals);
}

// P55-02 (2026-04-28): split the per-gate review surface into two
// layers, modeled on Stately Studio's always-on semantic indicators
// + on-demand inspector glow:
//
//   Layer 1 — `applyGateProposalMarkers(proposals)`
//     Always-on, regardless of review-mode. Paints a small Stately-
//     style accent marker on any gate carrying ≥1 OPEN proposal,
//     with the count rendered when count > 1. Click opens the
//     approve drawer + spotlights the matching ticket card. This is
//     what an engineer sees the instant the page loads — semantic
//     "this gate has open work" at a glance, no toggle needed.
//
//   Layer 2 — `applyReviewSpotlight(proposals)`
//     Gated by body[data-review-mode="on"]. Adds the heavier glow +
//     pulse (the auditor's "reviewing now" lens). Preserved from
//     P44-04 unchanged in behavior.
//
// The legacy `applyReviewAnchors(...)` entry point remains as a
// thin wrapper that calls both — every existing call site stays
// correct without churn.
//
// Codex P55-02 round-4 P2: the wrapper consults the freshness flag.
// If proposals are stale (fetch failed, or refresh in progress), we
// pass [] to both layers so they tear down their DOM rather than
// repainting from stale `_latestProposals`. setReviewMode() and
// circuit re-hydration both call us with `_latestProposals`, and
// without this gate they'd resurrect just-cleared markers.
function applyReviewAnchors(proposals) {
  if (!_proposalsAreFresh) {
    applyGateProposalMarkers([]);
    applyReviewSpotlight([]);
    return;
  }
  applyGateProposalMarkers(proposals);
  applyReviewSpotlight(proposals);
}

// Layer 1: always-on markers. Stately-style.
function applyGateProposalMarkers(proposals) {
  const mount = document.getElementById("workbench-circuit-hero-mount");
  if (!mount) return;
  // Tear down prior markers so a refresh reflects the current
  // OPEN-ticket set, not a stale superset.
  for (const m of mount.querySelectorAll(".workbench-gate-proposal-marker")) {
    m.remove();
  }
  // Codex P55-04 round-1 P2: dismiss the shared hover popover. Its
  // SVG-marker anchor was just torn down — leaving the popover
  // visible would float a stale overlay over the canvas/drawer
  // until the user happens to mouseleave the popover region.
  hideGateMarkerPopover();
  // Compute per-gate OPEN-ticket counts.
  const counts = computeOpenProposalCountsByGate(proposals);
  for (const [gateId, count] of counts) {
    const useEl = mount.querySelector(`use[data-gate-id="${gateId}"]`);
    if (!useEl || !useEl.ownerSVGElement) continue;
    const x = parseFloat(useEl.getAttribute("x") || "0");
    const y = parseFloat(useEl.getAttribute("y") || "0");
    const w = parseFloat(useEl.getAttribute("width") || "0");
    // Marker = a small rounded rect with the count, anchored at the
    // top-right corner of the gate. Group <g> so we can wire one
    // click handler across both the rect + label child elements.
    const NS = "http://www.w3.org/2000/svg";
    const group = document.createElementNS(NS, "g");
    group.setAttribute("class", "workbench-gate-proposal-marker");
    group.setAttribute("data-marker-for", gateId);
    group.setAttribute("data-open-count", String(count));
    // Codex P55-04 round-3 P3: a11y label via aria-label rather than
    // a child <title>. The <title> element triggers a NATIVE browser
    // tooltip after a short hover delay, which competes with the
    // P55-04 popover (the engineer pauses on the marker, custom card
    // appears, then the native tooltip pops on top and obscures the
    // first rows). aria-label gives screen readers an accessible
    // name without invoking the OS tooltip layer.
    group.setAttribute("role", "button");
    group.setAttribute(
      "aria-label",
      count === 1
        ? `${count} 个待审工单 · 1 OPEN proposal — 点击审阅 / click to review`
        : `${count} 个待审工单 · ${count} OPEN proposals — 点击审阅 / click to review`,
    );
    // Marker geometry. Right edge of gate, slightly above the top-right corner.
    const markerW = count > 9 ? 18 : 14;
    const markerH = 14;
    const markerX = x + w - markerW + 6;
    const markerY = y - 6;
    const rect = document.createElementNS(NS, "rect");
    rect.setAttribute("class", "workbench-gate-proposal-marker-bg");
    rect.setAttribute("x", String(markerX));
    rect.setAttribute("y", String(markerY));
    rect.setAttribute("width", String(markerW));
    rect.setAttribute("height", String(markerH));
    rect.setAttribute("rx", "3");
    rect.setAttribute("ry", "3");
    group.appendChild(rect);
    const label = document.createElementNS(NS, "text");
    label.setAttribute("class", "workbench-gate-proposal-marker-label");
    label.setAttribute("x", String(markerX + markerW / 2));
    label.setAttribute("y", String(markerY + markerH / 2 + 0.5));
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("dominant-baseline", "middle");
    label.textContent = String(count);
    group.appendChild(label);
    // Click → open approve drawer + spotlight.
    group.addEventListener("click", (e) => {
      e.stopPropagation();
      // Codex P55-04 round-1 P2: dismiss the popover before the
      // drawer slides in — otherwise the fixed-position overlay
      // floats above the drawer until the user happens to leave
      // its hover region.
      hideGateMarkerPopover();
      openApproveDrawerAndSpotlight(gateId);
    });
    useEl.ownerSVGElement.appendChild(group);
  }
  // P55-04: re-wire hover previews against the freshly-rendered
  // markers. Old markers (and their listeners) were torn down at
  // the top of this function; new markers need fresh listeners.
  installGateMarkerHoverPreviews();
}

// ─────────────────────────────────────────────────────────────────
// P55-04 (2026-04-28): Figma-style hover preview popover.
//
// Hover over a P55-02 marker → small floating card listing every
// OPEN proposal for that gate (author, role, age, summary). Click a
// row → opens the approve drawer + spotlights THAT specific
// proposal (not the gate-wide first OPEN). Mouseleave with a 200ms
// grace period so the user can move pointer marker → popover
// without it vanishing under their cursor.
// ─────────────────────────────────────────────────────────────────

let _gateMarkerPopoverHideTimer = null;

// Codex P55-04 round-1 P2: shared hide helper. Used by:
//   - mouseleave grace-period timeout (the normal hide path)
//   - marker click (drawer is about to open; don't float over it)
//   - applyGateProposalMarkers tear-down (anchor disappeared)
// Centralizing also clears any pending grace timer so a queued
// hide doesn't stomp a subsequent show.
function hideGateMarkerPopover() {
  const popover = document.getElementById("workbench-gate-marker-popover");
  if (!popover) return;
  if (_gateMarkerPopoverHideTimer) {
    clearTimeout(_gateMarkerPopoverHideTimer);
    _gateMarkerPopoverHideTimer = null;
  }
  popover.hidden = true;
  popover.setAttribute("aria-hidden", "true");
}

function installGateMarkerHoverPreviews() {
  const popover = document.getElementById("workbench-gate-marker-popover");
  if (!popover) return;
  const mount = document.getElementById("workbench-circuit-hero-mount");
  if (!mount) return;
  // Wire each marker. (applyGateProposalMarkers tears down + rebuilds
  // markers each refresh, so we re-wire fresh listeners every time.)
  for (const marker of mount.querySelectorAll(".workbench-gate-proposal-marker")) {
    const gateId = marker.getAttribute("data-marker-for");
    if (!gateId) continue;
    marker.addEventListener("mouseenter", () => {
      if (_gateMarkerPopoverHideTimer) {
        clearTimeout(_gateMarkerPopoverHideTimer);
        _gateMarkerPopoverHideTimer = null;
      }
      renderGateMarkerPopover(gateId);
      // Position the popover relative to the marker's viewport rect.
      const rect = marker.getBoundingClientRect();
      // Anchor: just below + slightly right of the marker so it
      // doesn't cover the gate label. Clamp to viewport so the
      // popover doesn't spill off the right OR bottom edges.
      const margin = 8;
      const popWidth = 280; // Matches the CSS max-width.
      let left = rect.right + margin;
      const viewportRight = window.innerWidth - margin;
      if (left + popWidth > viewportRight) {
        left = Math.max(margin, rect.left - popWidth - margin);
      }
      // Codex P55-04 round-2 P2: clamp `top` to window.innerHeight.
      // The popover can be up to 360px tall (CSS max-height), so a
      // low-y marker (L4 near the bottom of a 640px SVG) on a
      // laptop-height viewport would otherwise spill off-screen
      // and hide later proposal rows. Unhide first so offsetHeight
      // reads the rendered height; then if it would overflow the
      // bottom, flip to render ABOVE the marker (rect.top - h - margin).
      popover.style.left = `${left}px`;
      popover.style.top = `${rect.bottom + margin}px`;
      popover.hidden = false;
      popover.setAttribute("aria-hidden", "false");
      const popHeight = popover.offsetHeight;
      const viewportBottom = window.innerHeight - margin;
      let top = rect.bottom + margin;
      if (top + popHeight > viewportBottom) {
        // Try flipping above the marker.
        const flipped = rect.top - margin - popHeight;
        top = flipped >= margin
          ? flipped
          : Math.max(margin, viewportBottom - popHeight);
      }
      popover.style.top = `${top}px`;
    });
    marker.addEventListener("mouseleave", () => {
      _gateMarkerPopoverHideTimer = setTimeout(() => {
        popover.hidden = true;
        popover.setAttribute("aria-hidden", "true");
        _gateMarkerPopoverHideTimer = null;
      }, 200);
    });
  }
  // Pointer entering the popover itself cancels any pending hide
  // (so users can interact with the rows without the popover dying
  // under their cursor).
  if (!popover.dataset.hoverWired) {
    popover.dataset.hoverWired = "1";
    popover.addEventListener("mouseenter", () => {
      if (_gateMarkerPopoverHideTimer) {
        clearTimeout(_gateMarkerPopoverHideTimer);
        _gateMarkerPopoverHideTimer = null;
      }
    });
    popover.addEventListener("mouseleave", () => {
      _gateMarkerPopoverHideTimer = setTimeout(() => {
        popover.hidden = true;
        popover.setAttribute("aria-hidden", "true");
        _gateMarkerPopoverHideTimer = null;
      }, 200);
    });
    // Codex P55-04 round-3 P3: hide on scroll/resize. The popover
    // is fixed-position; if the viewport changes after positioning,
    // it stays at the old coordinates and detaches from the marker
    // it was anchored to. Hiding is the cheapest correct response —
    // the user can re-hover for a fresh anchor. capture: true so
    // we hear the scroll even when nested scroll containers fire it.
    const onViewportChange = () => {
      if (!popover.hidden) {
        hideGateMarkerPopover();
      }
    };
    window.addEventListener("scroll", onViewportChange, { capture: true, passive: true });
    window.addEventListener("resize", onViewportChange, { passive: true });
  }
}

function renderGateMarkerPopover(gateId) {
  const popover = document.getElementById("workbench-gate-marker-popover");
  if (!popover) return;
  const proposals = (_latestProposals || []).filter(
    (p) =>
      p.status === "OPEN" &&
      ((p.interpretation && p.interpretation.affected_gates) || []).includes(
        gateId,
      ),
  );
  const escape = (text) =>
    String(text == null ? "" : text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  const header =
    `<div class="workbench-gate-marker-popover-header">` +
    `<span class="workbench-gate-marker-popover-gate">${escape(gateId)}</span>` +
    `<span class="workbench-gate-marker-popover-count">` +
    `${proposals.length} 个待审 · ${proposals.length} OPEN` +
    `</span>` +
    `</div>`;
  const rows = proposals
    .map((p) => {
      const author = p.author_name || "anonymous";
      const role = p.author_role || "";
      const interp = p.interpretation || {};
      const summary =
        interp.summary_zh || interp.summary_en || p.source_text || "";
      const age = formatRelativeAge(p.created_at);
      // Avatar = first 2 chars of author name in a colored circle
      // tinted by hash(name) % 360 hue.
      const initials = author.slice(0, 2).toUpperCase();
      const hue = avatarHueForName(author);
      return (
        `<button class="workbench-gate-marker-popover-row" ` +
        `data-proposal-id="${escape(p.id)}" ` +
        `type="button">` +
        `<span class="workbench-gate-marker-popover-avatar" ` +
        `style="--avatar-hue:${hue}">${escape(initials)}</span>` +
        `<span class="workbench-gate-marker-popover-meta">` +
        `<span class="workbench-gate-marker-popover-author">` +
        `${escape(author)}` +
        (role ? ` <em>· ${escape(role)}</em>` : "") +
        `</span>` +
        `<span class="workbench-gate-marker-popover-age">${escape(age)}</span>` +
        `</span>` +
        `<span class="workbench-gate-marker-popover-summary">` +
        `${escape(summary)}` +
        `</span>` +
        `</button>`
      );
    })
    .join("");
  popover.innerHTML = header + rows;
  // Wire row clicks: open drawer + spotlight THAT specific proposal.
  for (const row of popover.querySelectorAll(".workbench-gate-marker-popover-row")) {
    row.addEventListener("click", (e) => {
      e.stopPropagation();
      const proposalId = row.getAttribute("data-proposal-id");
      const dockBtn = document.querySelector(
        '#workbench-dock [data-dock-target="approve"]',
      );
      const isOpen =
        document.body.getAttribute("data-active-tool") === "approve";
      if (dockBtn && !isOpen) {
        dockBtn.click();
      }
      // Hide the popover so it doesn't linger over the drawer.
      hideGateMarkerPopover();
      setTimeout(() => {
        if (proposalId) {
          spotlightInboxByProposalId(proposalId);
        }
      }, 220);
    });
  }
}

// Hash a name into a stable hue (0-359). Same name across sessions
// gets the same avatar color; different authors get distinct hues
// without us hand-maintaining a palette.
function avatarHueForName(name) {
  let h = 0;
  const s = String(name || "");
  for (let i = 0; i < s.length; i++) {
    h = (h * 31 + s.charCodeAt(i)) | 0;
  }
  return Math.abs(h) % 360;
}

// Relative age formatter: "5m ago" / "2h ago" / "3d ago" / "Apr 26"
// for older. Single helper so future surfaces stay consistent.
function formatRelativeAge(iso) {
  if (!iso) return "";
  const then = new Date(iso).getTime();
  if (!Number.isFinite(then)) return "";
  const now = Date.now();
  const diffMs = now - then;
  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return "just now · 刚刚";
  if (minutes < 60) return `${minutes}m ago · ${minutes}分钟前`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago · ${hours}小时前`;
  const days = Math.floor(hours / 24);
  if (days < 14) return `${days}d ago · ${days}天前`;
  // Older — fall back to absolute Mon DD.
  const d = new Date(then);
  const months = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
  ];
  return `${months[d.getMonth()]} ${d.getDate()}`;
}

// P55-03 (2026-04-28): fan-in count badge. Always-on, structural —
// pairs with the P55-02 proposal marker on the OPPOSITE corner of
// each gate so an engineer absorbs both pieces of element-level
// metadata at-a-glance:
//
//   top-RIGHT — P55-02 OPEN-proposal count (state, filled accent)
//   top-LEFT  — P55-03 fan-in count        (structure, outline-only)
//
// Reads the count from the SVG's data-input-count attribute (single
// source of truth — fantui_circuit.html). Skips count < 2 because a
// single-input "gate" is a passthrough and the badge would be noise.
function applyGateFanInBadges() {
  const mount = document.getElementById("workbench-circuit-hero-mount");
  if (!mount) return;
  // Idempotency: a system switch re-hydrates the SVG and re-invokes
  // this function — clear prior badges so we don't duplicate.
  for (const b of mount.querySelectorAll(".workbench-gate-fan-in-badge")) {
    b.remove();
  }
  const useEls = mount.querySelectorAll("use[data-gate-id][data-input-count]");
  for (const useEl of useEls) {
    if (!useEl.ownerSVGElement) continue;
    const gateId = useEl.getAttribute("data-gate-id");
    const count = parseInt(useEl.getAttribute("data-input-count") || "0", 10);
    // Single-input passthroughs don't merit a "1" decoration.
    if (!Number.isFinite(count) || count < 2) continue;
    const x = parseFloat(useEl.getAttribute("x") || "0");
    const y = parseFloat(useEl.getAttribute("y") || "0");
    const NS = "http://www.w3.org/2000/svg";
    const group = document.createElementNS(NS, "g");
    group.setAttribute("class", "workbench-gate-fan-in-badge");
    group.setAttribute("data-fan-in-for", gateId);
    group.setAttribute("data-fan-in-count", String(count));
    const title = document.createElementNS(NS, "title");
    title.textContent = `${count} 路输入 · ${count}-input gate (fan-in)`;
    group.appendChild(title);
    // Geometry: left-overhanging mirror of the proposal marker.
    // The proposal marker overhangs the gate's right edge; this
    // badge overhangs the LEFT edge by the same 6px so an engineer
    // reads both corners as a balanced pair.
    const badgeW = count > 9 ? 16 : 12;
    const badgeH = 12;
    const badgeX = x - 6;
    const badgeY = y - 6;
    const rect = document.createElementNS(NS, "rect");
    rect.setAttribute("class", "workbench-gate-fan-in-badge-bg");
    rect.setAttribute("x", String(badgeX));
    rect.setAttribute("y", String(badgeY));
    rect.setAttribute("width", String(badgeW));
    rect.setAttribute("height", String(badgeH));
    rect.setAttribute("rx", "2");
    rect.setAttribute("ry", "2");
    group.appendChild(rect);
    const label = document.createElementNS(NS, "text");
    label.setAttribute("class", "workbench-gate-fan-in-badge-label");
    label.setAttribute("x", String(badgeX + badgeW / 2));
    label.setAttribute("y", String(badgeY + badgeH / 2 + 0.5));
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("dominant-baseline", "middle");
    label.textContent = String(count);
    group.appendChild(label);
    // Codex P55-03 round-2 P3: the rect's pointer-events: stroke
    // means a click on the 1px outline gets caught by the badge.
    // Without forwarding, that thin zone becomes a dead spot for
    // the gate's own click handler (spotlightInboxByGate when
    // review mode is on). Forward to spotlightCircuitGate (a benign
    // visual self-highlight) so any click in the badge zone gives
    // immediate, consistent feedback no matter what the gate's
    // current handler chain is.
    group.addEventListener("click", (e) => {
      e.stopPropagation();
      spotlightCircuitGate(gateId);
    });
    useEl.ownerSVGElement.appendChild(group);
  }
}

// Layer 2: review-mode spotlight (preserved from P44-04).
function applyReviewSpotlight(proposals) {
  const mount = document.getElementById("workbench-circuit-hero-mount");
  if (!mount) return;
  for (const el of mount.querySelectorAll(".is-review-anchor")) {
    el.classList.remove("is-review-anchor");
  }
  if (document.body.getAttribute("data-review-mode") !== "on") return;
  const counts = computeOpenProposalCountsByGate(proposals);
  for (const [gateId] of counts) {
    const targets = mount.querySelectorAll(`[data-gate-id="${gateId}"]`);
    if (targets.length === 0) continue;
    for (const el of targets) {
      el.classList.add("is-review-anchor");
      if (!el.dataset.reviewAnchorClickWired) {
        el.dataset.reviewAnchorClickWired = "1";
        el.addEventListener("click", () => spotlightInboxByGate(gateId));
      }
    }
  }
}

// Pure helper: aggregates OPEN-ticket counts per gate from the
// latest proposal set. Extracted so both layers + tests can reuse.
function computeOpenProposalCountsByGate(proposals) {
  const counts = new Map();
  for (const p of proposals || []) {
    if (p.status !== "OPEN") continue;
    const gates = (p.interpretation && p.interpretation.affected_gates) || [];
    for (const g of gates) {
      counts.set(g, (counts.get(g) || 0) + 1);
    }
  }
  return counts;
}

// P55-02: marker click → ensure approve drawer is open, then
// spotlight the inbox card. Reuses the existing dock-target wiring
// (clicking the dock's "approve" button is what opens the drawer)
// and the existing spotlight helper. If the drawer is already open
// nothing happens visually; the spotlight is the affordance.
//
// Codex P55-02 round-1 P3: capture the target proposal id
// synchronously at click time. The 220ms timeout (drawer slide-in
// motion token) is long enough for proposals to refresh or the
// reviewer to switch systems — re-resolving inside the timeout
// would race against a mutated _latestProposals and scroll to the
// wrong card (or none). Snapshotting the id at click is
// deterministic.
function openApproveDrawerAndSpotlight(gateId) {
  const dockBtn = document.querySelector(
    '#workbench-dock [data-dock-target="approve"]'
  );
  const isOpen =
    document.body.getAttribute("data-active-tool") === "approve";
  if (dockBtn && !isOpen) {
    dockBtn.click();
  }
  const targetProposalId = resolveProposalIdForGate(gateId);
  // Spotlight after the drawer's slide-in finishes (168ms motion
  // token from P52-02). Wait a bit longer to let the inbox render.
  setTimeout(() => {
    if (targetProposalId) {
      spotlightInboxByProposalId(targetProposalId);
    }
  }, 220);
}

function resolveProposalIdForGate(gateId) {
  const target = (_latestProposals || []).find(
    (p) =>
      p.status === "OPEN" &&
      ((p.interpretation && p.interpretation.affected_gates) || []).includes(
        gateId,
      ),
  );
  return target ? target.id : null;
}

function spotlightInboxByProposalId(proposalId) {
  const list = document.getElementById("annotation-inbox-list");
  if (!list) return;
  const card = list.querySelector(`[data-proposal-id="${proposalId}"]`);
  if (!card) return;
  for (const c of list.querySelectorAll(".is-review-spotlight")) {
    c.classList.remove("is-review-spotlight");
  }
  void card.getBoundingClientRect();
  card.classList.add("is-review-spotlight");
  setTimeout(() => card.classList.remove("is-review-spotlight"), 1500);
  if (typeof card.scrollIntoView === "function") {
    card.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}

function spotlightCircuitGate(gateId) {
  const mount = document.getElementById("workbench-circuit-hero-mount");
  if (!mount) return;
  for (const el of mount.querySelectorAll(`[data-gate-id="${gateId}"]`)) {
    el.classList.remove("is-review-spotlight");
    // Force reflow so the animation restarts on rapid re-clicks.
    void el.getBoundingClientRect();
    el.classList.add("is-review-spotlight");
    setTimeout(() => el.classList.remove("is-review-spotlight"), 1500);
  }
  const useEl = mount.querySelector(`use[data-gate-id="${gateId}"]`);
  if (useEl && typeof useEl.scrollIntoView === "function") {
    useEl.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}

function spotlightInboxByGate(gateId) {
  const proposalId = resolveProposalIdForGate(gateId);
  if (proposalId) {
    spotlightInboxByProposalId(proposalId);
  }
}

// ─────────────────────────────────────────────────────────────────
// P44-05 (2026-04-26): accept / reject + dev-queue handoff.
//
// Reviewer clicks ✅ / ✕ on a ticket card → POST to
// /api/proposals/<id>/<accept|reject>. The server flips status,
// appends an audit-trail history entry, and (on accept) writes a
// markdown handoff brief Claude Code's /gsd-execute-phase reads in a
// later session. We re-fetch the inbox so the status pill flips
// (and the now-terminal ticket loses its action buttons) without a
// page reload. Anchors auto-update because applyReviewAnchors only
// counts OPEN tickets — the accepted gate stops glowing as soon as
// it has no open tickets left.
// ─────────────────────────────────────────────────────────────────

async function transitionProposal(proposalId, action) {
  if (!proposalId || (action !== "accept" && action !== "reject")) return;
  const identity = document.getElementById("workbench-identity");
  const actor = identity
    ? identity.getAttribute("data-identity-name") || "anonymous"
    : "anonymous";
  let note = null;
  if (action === "reject") {
    // Cheap free-form reason capture — keeps the audit trail useful
    // without bolting on a modal. Empty/cancelled = no note.
    const reason = window.prompt(
      "驳回理由（可选）· Rejection reason (optional):",
      "",
    );
    if (reason && reason.trim()) {
      note = reason.trim();
    }
  }
  try {
    const response = await fetch(`${PROPOSALS_PATH}/${encodeURIComponent(proposalId)}/${action}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ actor, note }),
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    await loadProposalsInbox();
  } catch (error) {
    // Surface the error inline on the suggestion-status row so it
    // shows up wherever the reviewer is looking. Fine to share with
    // the engineer-side status field — no engineer action is
    // running at the same moment.
    const status = document.getElementById("workbench-suggestion-status");
    if (status) {
      status.dataset.status = "error";
      status.textContent = `${action} 失败 · ${action} failed: ${error.message || error}`;
    }
  }
}

// ─────────────────────────────────────────────────────────────────
// P44-06 (2026-04-26): panel version chip + rollback hints.
//
// The chip surfaces "what version of the panel am I looking at" =
// truth-engine HEAD SHA + count of ACCEPTED proposals. Click → jump
// to the inbox so the engineer can skim the decision history. The
// rollback-hints expander lives inside each ACCEPTED ticket card and
// reveals the exact git commands the engineer would run themselves
// to revert that proposal's commit. The workbench never executes
// git mutations; the hints are pure read-only instruction (truth
// engine red line stays intact).
// ─────────────────────────────────────────────────────────────────

const STATE_OF_WORLD_PATH = "/api/workbench/state-of-world";

let _panelVersionSha = null;

function installPanelVersionChip() {
  const chip = document.getElementById("workbench-panel-version-chip");
  if (!chip) return;
  chip.addEventListener("click", () => {
    const inbox = document.getElementById("annotation-inbox");
    if (inbox && typeof inbox.scrollIntoView === "function") {
      inbox.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
  // Fire both fetches in parallel so the chip flips from loading →
  // ready in one tick. The proposals fetch is ALREADY in flight via
  // installProposalInbox() above; we just need its count, which the
  // inbox loader stashes via _latestProposals + invokes
  // refreshPanelVersionChip(). Here we only need the SHA.
  fetch(STATE_OF_WORLD_PATH)
    .then((r) => (r.ok ? r.json() : null))
    .then((body) => {
      _panelVersionSha = (body && body.truth_engine_sha) || null;
      refreshPanelVersionChip();
      // P47-01: render the per-namespace lineage rows.
      const namespaces = (body && body.panel_namespaces) || [];
      renderPanelNamespaces(namespaces);
    })
    .catch(() => {
      const chip2 = document.getElementById("workbench-panel-version-chip");
      if (chip2) {
        chip2.setAttribute("data-panel-version-state", "error");
        const label = chip2.querySelector("[data-panel-version-label]");
        if (label) label.textContent = "—";
      }
      // P47-01: surface namespace fetch error too — empty is not the same
      // as failed; the engineer should know the lineage view is unavailable.
      const ns = document.getElementById("workbench-panel-namespaces");
      if (ns) {
        ns.setAttribute("data-panel-namespaces-state", "error");
        ns.hidden = false;
        ns.innerHTML =
          `<span class="workbench-panel-namespace-row" data-panel-namespace="error">` +
          `<span class="ns-label">命名空间血缘 · namespace lineage:</span>` +
          `<span class="ns-subject">— (state-of-world fetch failed)</span>` +
          `</span>`;
      }
    });
}

// P47-01 (2026-04-27): render per-namespace last-touch rows.
//
// Three rows in fixed order — logic_truth / requirements /
// simulation_workbench — each showing label + short_sha + commit
// subject (truncated). Subject is also surfaced as title for the
// hover full text + commit time. Click on a row jumps to the inbox
// (same destination as the main chip) so the engineer can scroll
// through the decision history.
function renderPanelNamespaces(namespaces) {
  const container = document.getElementById("workbench-panel-namespaces");
  if (!container) return;
  if (!Array.isArray(namespaces) || namespaces.length === 0) {
    container.hidden = true;
    return;
  }
  const escape = (text) =>
    String(text == null ? "" : text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  const rows = namespaces.map((ns) => {
    const namespace = escape(ns.namespace || "");
    const labelZh = escape(ns.label_zh || ns.namespace || "");
    const labelEn = escape(ns.label_en || "");
    const sha = escape(ns.head_sha || "—");
    const subject = escape(ns.head_subject || "—");
    const committedAt = escape(ns.head_committed_at || "—");
    const tooltip = escape(`${ns.head_subject || "—"} · ${ns.head_committed_at || "—"}`);
    return (
      `<span class="workbench-panel-namespace-row"` +
      ` data-panel-namespace="${namespace}"` +
      ` title="${tooltip}">` +
      `<span class="ns-label">${labelZh} · ${labelEn}</span>` +
      `<span class="ns-sha">${sha}</span>` +
      `<span class="ns-subject">${subject}</span>` +
      `</span>`
    );
  });
  container.innerHTML = rows.join("");
  container.setAttribute("data-panel-namespaces-state", "ready");
  container.hidden = false;
}

function refreshPanelVersionChip() {
  const chip = document.getElementById("workbench-panel-version-chip");
  if (!chip) return;
  const label = chip.querySelector("[data-panel-version-label]");
  if (!label) return;
  const accepted = (_latestProposals || []).filter((p) => p.status === "ACCEPTED").length;
  if (_panelVersionSha == null) {
    // SHA fetch not back yet — show count alone so the chip still
    // updates the moment the inbox arrives.
    label.textContent = `… · ${accepted} 已通过 · accepted`;
    return;
  }
  chip.setAttribute("data-panel-version-state", "ready");
  label.textContent = `${_panelVersionSha} · ${accepted} 已通过 · accepted`;
}

function renderRollbackHints(proposal) {
  const escape = (text) =>
    String(text == null ? "" : text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  const id = escape(proposal.id);
  // The brief filename matches the proposal id by construction
  // (see write_dev_queue_brief in demo_server.py). The grep pattern
  // matches both PR titles ("...PROP-XXX...") and dev-queue brief
  // mentions, so the engineer can find the commit regardless of
  // whether Claude Code referenced the brief or the proposal id in
  // its commit message.
  return (
    `<p>找到并回滚此提议对应的真值引擎提交 · Find &amp; revert this proposal's truth-engine commit:</p>` +
    `<code>git log --oneline --all --grep="${id}"</code>` +
    `<code>git revert &lt;sha-from-above&gt;</code>` +
    `<p>或查看本提议的 dev-queue 简报 · Or inspect this proposal's dev-queue brief:</p>` +
    `<code>cat .planning/dev_queue/${id}.md</code>` +
    `<p style="margin-top:0.45rem;color:rgba(206,223,236,0.7);">` +
    `工作台只读，不会替你执行 git 命令；请在终端确认无误后再回滚 ·` +
    ` Workbench is read-only and will never run git for you;` +
    ` confirm the SHA in your terminal before reverting.` +
    `</p>`
  );
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

  container.replaceChildren(...documents.map((doc) => {
    const card = document.createElement("article");
    card.className = "workbench-fingerprint-item";

    const header = document.createElement("div");
    header.className = "workbench-fingerprint-item-header";

    const title = document.createElement("strong");
    title.className = "workbench-fingerprint-item-title";
    title.textContent = doc.title || doc.id || "未命名文档";

    const chips = document.createElement("div");
    chips.className = "workbench-fingerprint-chip-row";
    chips.append(
      createFingerprintChip(documentKindLabel(doc.kind), "source"),
      createFingerprintChip(documentRoleLabel(doc.role), "role"),
    );

    header.append(title, chips);

    const location = document.createElement("p");
    location.className = "workbench-fingerprint-item-detail";
    location.textContent = doc.location || "未提供路径";

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
  const documentKinds = uniqueValues(documents.map((doc) => doc.kind));
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
      label.textContent = mode === "truth_engine" ? "真值引擎 · Truth Engine" : "手动（仅参考）· Manual (advisory)";
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

// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
// Mirrors BEAT_DEEP_PAYLOAD from tests/e2e/test_wow_a_causal_chain.py:51 and
// the monte-carlo / reverse-diagnose API contracts from the matching e2e
// suites. One click → POST (with bounded timeout) → single-line summary in
// the card's result area.
//
// The exact card payloads are FROZEN — tests/test_workbench_wow_starters.py
// asserts byte-equality against this object; do not silently re-tune
// n_trials, max_results, n1k, or BEAT_DEEP_PAYLOAD shape without updating
// the regression lock and the surface-inventory drift acceptance.
const WOW_REQUEST_TIMEOUT_MS = 10000;

const WOW_SCENARIOS = {
  wow_a: {
    endpoint: "/api/lever-snapshot",
    // BEAT_DEEP_PAYLOAD per tests/e2e/test_wow_a_causal_chain.py:51
    payload: {
      tra_deg: -35,
      radio_altitude_ft: 2,
      engine_running: true,
      aircraft_on_ground: true,
      reverser_inhibited: false,
      eec_enable: true,
      n1k: 0.92,
      feedback_mode: "auto_scrubber",
      deploy_position_percent: 95,
    },
    // P1+P2+P5 R2 fix: read actual logic-gate states from the response
    // instead of overstating "L1–L4 latched". Under auto_scrubber pullback
    // the e2e contract says BEAT_DEEP latches at minimum {logic2, logic3,
    // logic4} with logic1 dropping out (reverser_not_deployed_eec flips
    // false mid-deploy). Print the live active set verbatim so the card
    // never overstates the truth.
    summarize: (body) => {
      const logic = body && typeof body.logic === "object" ? body.logic : {};
      const order = ["logic1", "logic2", "logic3", "logic4"];
      const active = order.filter((k) => logic[k] && logic[k].active === true);
      const nodes = Array.isArray(body && body.nodes) ? body.nodes : [];
      const activeStr = active.length === 0 ? "none" : active.join("+");
      return `nodes=${nodes.length} · active=[${activeStr}] · mode=auto_scrubber`;
    },
  },
  wow_b: {
    endpoint: "/api/monte-carlo/run",
    payload: { system_id: "thrust-reverser", n_trials: 1000, seed: 42 },
    summarize: (body) => {
      if (!body) return "(empty body)";
      const sr = typeof body.success_rate === "number" ? body.success_rate.toFixed(4) : body.success_rate;
      const failures = body.n_failures;
      const trials = body.n_trials;
      return `trials=${trials} · success_rate=${sr} · failures=${failures}`;
    },
  },
  wow_c: {
    endpoint: "/api/diagnosis/run",
    payload: { system_id: "thrust-reverser", outcome: "deploy_confirmed", max_results: 10 },
    summarize: (body) => {
      if (!body) return "(empty body)";
      const total = body.total_combos_found;
      const returned = Array.isArray(body.results) ? body.results.length : 0;
      const grid = body.grid_resolution;
      return `outcome=${body.outcome} · total_combos=${total} · returned=${returned} · grid=${grid}`;
    },
  },
};

async function runWowScenario(wowId) {
  const scenario = WOW_SCENARIOS[wowId];
  const button = document.querySelector(
    `.workbench-wow-run-button[data-wow-id="${wowId}"]`,
  );
  const result = document.querySelector(
    `.workbench-wow-result[data-wow-result-for="${wowId}"]`,
  );
  if (!scenario || !result) {
    return;
  }
  if (button) {
    button.disabled = true;
  }
  result.removeAttribute("data-wow-state");
  result.textContent = `POST ${scenario.endpoint} ...`;
  // P1 R2 BLOCKER fix: bounded timeout via AbortController so a stalled
  // endpoint cannot freeze the card mid-demo.
  const controller =
    typeof AbortController !== "undefined" ? new AbortController() : null;
  const timeoutHandle = controller
    ? setTimeout(() => controller.abort(), WOW_REQUEST_TIMEOUT_MS)
    : null;
  try {
    const t0 = performance.now();
    const response = await fetch(scenario.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(scenario.payload),
      signal: controller ? controller.signal : undefined,
    });
    const ms = Math.round(performance.now() - t0);
    let body = null;
    try {
      body = await response.json();
    } catch (_err) {
      body = null;
    }
    if (!response.ok) {
      result.setAttribute("data-wow-state", "error");
      const errMsg = body && body.error ? body.error : `HTTP ${response.status}`;
      result.textContent = `${response.status} · ${errMsg} · ${ms}ms`;
      return;
    }
    result.setAttribute("data-wow-state", "ok");
    result.textContent = `200 OK · ${scenario.summarize(body)} · ${ms}ms`;
  } catch (err) {
    result.setAttribute("data-wow-state", "error");
    if (err && err.name === "AbortError") {
      result.textContent = `timed out after ${WOW_REQUEST_TIMEOUT_MS}ms · click again to retry`;
    } else {
      result.textContent = `network error: ${err && err.message ? err.message : err}`;
    }
  } finally {
    if (timeoutHandle !== null) {
      clearTimeout(timeoutHandle);
    }
    if (button) {
      button.disabled = false;
    }
  }
}

function installWowStarters() {
  const buttons = document.querySelectorAll(
    '.workbench-wow-run-button[data-wow-action="run"]',
  );
  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const wowId = btn.getAttribute("data-wow-id");
      if (wowId && WOW_SCENARIOS[wowId]) {
        void runWowScenario(wowId);
      }
    });
  });
}

// E11-08 (2026-04-26): role affordance.
// When the workbench identity is NOT Kogami, replace the Approval Center
// entry button + panel with an explicit "Pending Kogami sign-off"
// affordance instead of leaving disabled UI in place. setWorkbenchIdentity
// is exported on window for tests + URL-param-driven demo flow.
function applyRoleAffordance() {
  const chip = document.getElementById("workbench-identity");
  if (!chip) {
    return;
  }
  const identity = chip.getAttribute("data-identity-name") || "";
  const isKogami = identity.trim() === "Kogami";
  const entry = document.getElementById("approval-center-entry");
  const panel = document.getElementById("approval-center-panel");
  const affordance = document.getElementById(
    "workbench-pending-signoff-affordance",
  );
  if (entry) {
    entry.hidden = !isKogami;
    entry.setAttribute("aria-disabled", isKogami ? "false" : "true");
  }
  if (panel) {
    panel.hidden = !isKogami;
  }
  if (affordance) {
    affordance.setAttribute(
      "data-pending-signoff",
      isKogami ? "hidden" : "visible",
    );
  }
}

function setWorkbenchIdentity(name) {
  const chip = document.getElementById("workbench-identity");
  if (!chip || typeof name !== "string" || !name.trim()) {
    return false;
  }
  chip.setAttribute("data-identity-name", name.trim());
  const label = chip.querySelector("strong");
  if (label) {
    // Preserve the trailing role suffix (e.g., "/ Engineer") if present.
    const suffix = label.textContent.includes("/")
      ? label.textContent.split("/").slice(1).join("/").trimStart()
      : "";
    label.textContent = suffix ? `${name.trim()} / ${suffix}` : name.trim();
  }
  applyRoleAffordance();
  return true;
}

if (typeof window !== "undefined") {
  window.setWorkbenchIdentity = setWorkbenchIdentity;
}

// E11-06 (2026-04-26): hydrate the state-of-the-world status bar.
// Reads /api/workbench/state-of-world and writes the four advisory
// fields into the bar. Falls back to "—" so the page never shows a
// half-broken bar. Failures are silent (the bar starts with "…"
// placeholders so there is no flash of the wrong content).
const WORKBENCH_STATE_OF_WORLD_PATH = "/api/workbench/state-of-world";

async function hydrateStateOfWorldBar() {
  const bar = document.getElementById("workbench-state-of-world-bar");
  if (!bar) {
    return;
  }
  try {
    const response = await fetch(WORKBENCH_STATE_OF_WORLD_PATH, {
      method: "GET",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      return;
    }
    const payload = await response.json();
    const writeField = (key, value) => {
      const slot = bar.querySelector(`[data-sow-value="${key}"]`);
      if (slot) {
        slot.textContent =
          value === null || value === undefined || value === ""
            ? "—"
            : String(value);
      }
    };
    writeField("truth_engine_sha", payload.truth_engine_sha);
    writeField("recent_e2e_label", payload.recent_e2e_label);
    writeField("adversarial_label", payload.adversarial_label);
    writeField("open_known_issues_count", payload.open_known_issues_count);
  } catch (_err) {
    // Silent — the bar already shows "…" placeholders, which renders as
    // a benign "still loading" state instead of a broken half-page.
  }
}

window.addEventListener("DOMContentLoaded", () => {
  bootWorkbenchShell();
  installViewModeHandlers();
  installFeedbackModeAffordance();
  installWowStarters();
  installRecommendationCopyHandler();  // P59-03 work-order copy button
  void hydrateStateOfWorldBar();
  // E11-08: apply role affordance after DOM is ready. Honors
  // ?identity=<name> URL param so demos / tests can flip identity
  // without rebuilding the page.
  try {
    const params = new URLSearchParams(window.location.search);
    const requested = params.get("identity");
    if (requested && requested.trim()) {
      setWorkbenchIdentity(requested);
    } else {
      applyRoleAffordance();
    }
  } catch (_err) {
    applyRoleAffordance();
  }

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

// ─── P51-02: Live Log Panel SSE consumer ───────────────────────────
//
// Connects to /api/workbench/log-stream as soon as the panel exists.
// Renders a fixed-tail terminal view (last ~200 lines) with phase-
// driven coloring. Auto-reconnects after the server's 60s session
// window closes, carrying the cursor in `?since=N` so no events get
// dropped between reconnects.
//
// Why EventSource over fetch+ReadableStream: the stdlib EventSource
// handles reconnection, last-event-id, and message framing for free.
// All we provide is the data handler.

const WORKBENCH_LOG_STREAM_PATH = "/api/workbench/log-stream";
const LIVE_LOG_TAIL_MAX = 200;

let _wbLiveLogCursor = 0;
let _wbLiveLogSource = null;
let _wbLiveLogQueue = [];

function _wbLiveLogStatus(text) {
  const status = document.getElementById("workbench-live-log-status");
  if (status) status.textContent = text;
}

function _wbLiveLogRender() {
  const stream = document.getElementById("workbench-live-log-stream");
  if (!stream) return;
  const escape = (text) =>
    String(text == null ? "" : text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  const tail = _wbLiveLogQueue.slice(-LIVE_LOG_TAIL_MAX);
  stream.innerHTML = tail
    .map((ev) => {
      const ts = (ev.ts || "").slice(11, 19);  // HH:MM:SS
      const phase = (ev.phase || "—").padEnd(18);
      const level = (ev.level || "info").toUpperCase();
      return (
        `<span class="workbench-live-log-line" data-phase="${escape(ev.phase || "")}" data-level="${escape(ev.level || "info")}">` +
        `<span class="workbench-live-log-ts">${escape(ts)}</span> ` +
        `<span class="workbench-live-log-phase">${escape(phase)}</span> ` +
        `<span class="workbench-live-log-level">[${escape(level)}]</span> ` +
        `<span class="workbench-live-log-msg">${escape(ev.message || "")}</span>` +
        `</span>`
      );
    })
    .join("\n");
  stream.scrollTop = stream.scrollHeight;
}

function _wbLiveLogConnect() {
  if (_wbLiveLogSource) return;
  if (typeof EventSource === "undefined") {
    _wbLiveLogStatus("(EventSource unsupported)");
    return;
  }
  const url =
    WORKBENCH_LOG_STREAM_PATH + "?since=" + encodeURIComponent(_wbLiveLogCursor);
  let src;
  try {
    src = new EventSource(url);
  } catch (_) {
    _wbLiveLogStatus("connect failed");
    return;
  }
  _wbLiveLogSource = src;
  _wbLiveLogStatus("connecting…");
  src.addEventListener("open", () => _wbLiveLogStatus("connected"));
  src.addEventListener("message", (ev) => {
    let payload;
    try {
      payload = JSON.parse(ev.data);
    } catch (_) {
      return;
    }
    if (typeof payload.seq === "number") _wbLiveLogCursor = payload.seq;
    _wbLiveLogQueue.push(payload);
    if (_wbLiveLogQueue.length > LIVE_LOG_TAIL_MAX * 2) {
      _wbLiveLogQueue = _wbLiveLogQueue.slice(-LIVE_LOG_TAIL_MAX);
    }
    _wbLiveLogRender();
  });
  src.addEventListener("error", () => {
    _wbLiveLogStatus("reconnecting…");
    src.close();
    _wbLiveLogSource = null;
    // EventSource auto-reconnects on its own when we re-instantiate
    // it; do that after a brief delay so we don't tight-loop on
    // server-down.
    setTimeout(_wbLiveLogConnect, 2000);
  });
}

// Boot the panel if it exists. Don't crash on pages that don't
// include it (workbench_bundle.html, etc.).
(function _wbLiveLogBoot() {
  if (typeof document === "undefined") return;
  const panel = document.getElementById("workbench-live-log-panel");
  if (!panel) return;
  _wbLiveLogConnect();
})();

// ─── P52-01: tool dock + drawer wiring ─────────────────────────────
//
// Click a dock button → activate that tool. The CSS uses
// body[data-active-tool] to slide the matching `data-dock-section`
// in as a left-side drawer over the canvas. Clicking the active
// button again or pressing Esc dismisses the drawer.
//
// We deliberately don't move DOM nodes — the existing sections keep
// their original IDs/classes/positions. Activation just toggles
// visibility via the CSS rule `body[data-active-tool="X"]
// [data-dock-section="X"] { display: block; position: fixed; ... }`.

(function _wbDockBoot() {
  if (typeof document === "undefined") return;
  const dock = document.getElementById("workbench-dock");
  if (!dock) return;
  const buttons = Array.from(
    dock.querySelectorAll("[data-dock-target]")
  );
  if (buttons.length === 0) return;

  // P52-08: remember the dock button that opened the drawer so we
  // can return focus to it on close (keyboard users shouldn't get
  // bounced back to <body>).
  let lastDockTrigger = null;

  function _wbDrawerFocusEntry(tool) {
    if (!tool) return;
    // Activation flips `hidden` via CSS, but not until the next
    // paint — defer the focus call so the drawer is actually
    // focusable when we hit it.
    requestAnimationFrame(() => {
      const candidates = Array.from(
        document.querySelectorAll(`[data-dock-section="${tool}"]`)
      );
      const drawer = candidates.find((el) => !el.hidden) || candidates[0];
      if (!drawer) return;
      // Prefer the drawer's close button (canonical first focusable
      // landmark); fall back to the first focusable child or the
      // drawer itself with tabindex -1.
      const firstFocusable =
        drawer.querySelector("[data-dock-close]") ||
        drawer.querySelector(
          "input:not([disabled]), button:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex='-1'])"
        );
      if (firstFocusable) {
        firstFocusable.focus();
      } else {
        drawer.setAttribute("tabindex", "-1");
        drawer.focus();
      }
    });
  }

  function setActive(tool) {
    const previous = document.body.dataset.activeTool || "";
    document.body.dataset.activeTool = tool || "";
    for (const btn of buttons) {
      const isActive = btn.getAttribute("data-dock-target") === tool;
      btn.setAttribute("aria-pressed", isActive ? "true" : "false");
    }
    if (tool) {
      _wbDrawerFocusEntry(tool);
    } else if (previous && lastDockTrigger) {
      // Drawer just closed — return focus to whichever dock button
      // had opened it.
      lastDockTrigger.focus();
    }
  }

  for (const btn of buttons) {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-dock-target");
      const current = document.body.dataset.activeTool || "";
      if (target === current) {
        setActive("");  // click active button = close drawer
      } else {
        lastDockTrigger = btn;
        setActive(target);
      }
    });
  }

  // Drawer's close button (×). Multiple sections each have one;
  // event delegation keeps it simple.
  document.addEventListener("click", (ev) => {
    const target = ev.target;
    if (!(target instanceof HTMLElement)) return;
    if (target.matches("[data-dock-close]")) {
      setActive("");
    }
  });

  // Esc closes the drawer.
  document.addEventListener("keydown", (ev) => {
    if (ev.key === "Escape" && document.body.dataset.activeTool) {
      setActive("");
    }
  });
})();

// ─── P54-04 / P54-06: canvas-level system toggle (反推 / C919) ───────
//
// P54-04 introduced this as a circuit-only toggle. P54-06 promotes it
// to canvas-level: a single click swaps both (a) the legacy
// #workbench-system-select (which drives the circuit fragment fetch)
// and (b) the iframe srcs of the sim/cockpit/spec views — so the
// "4-piece set" is mirrored across both systems and the user sees a
// consistent set of surfaces no matter which system is active.
(function _wbCircuitSystemToggleBoot() {
  if (typeof document === "undefined") return;
  const toggle =
    document.getElementById("workbench-system-toggle") ||
    document.getElementById("workbench-circuit-system-toggle");
  if (!toggle) return;
  const buttons = Array.from(toggle.querySelectorAll("[data-circuit-system]"));
  if (buttons.length === 0) return;

  function swapIframes(system) {
    const iframes = document.querySelectorAll("iframe[data-system-iframe]");
    for (const frame of iframes) {
      const srcAttr = "data-system-src-" + system;
      const titleAttr = "data-system-title-" + system;
      const next = frame.getAttribute(srcAttr);
      const nextTitle = frame.getAttribute(titleAttr);

      // Keep the iframe title attr + the labelling <h2> in sync so
      // screen readers don't announce "Thrust-Reverser" while the
      // iframe is showing C919 content (Codex P54-06 review P3).
      if (nextTitle) {
        frame.setAttribute("title", nextTitle);
        const labelledById =
          frame.closest("section") &&
          frame.closest("section").getAttribute("aria-labelledby");
        if (labelledById) {
          const heading = document.getElementById(labelledById);
          if (heading) heading.textContent = nextTitle;
        }
      }

      if (!next) continue;
      // Compare against current src origin-relative path to avoid a
      // pointless reload when the user clicks the already-active pill.
      const currentTail = (frame.getAttribute("src") || "").split("?")[0];
      const nextTail = next.split("?")[0];
      if (currentTail === nextTail) continue;
      frame.setAttribute("src", next);
    }
  }

  function syncFromSelect() {
    const select = document.getElementById("workbench-system-select");
    const current = (select && select.value) || "thrust-reverser";
    for (const btn of buttons) {
      const isActive = btn.getAttribute("data-circuit-system") === current;
      btn.setAttribute("aria-pressed", isActive ? "true" : "false");
    }
    swapIframes(current);
  }

  for (const btn of buttons) {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-circuit-system");
      if (!target) return;
      const select = document.getElementById("workbench-system-select");
      if (select && select.value !== target) {
        select.value = target;
        select.dispatchEvent(new Event("change", { bubbles: true }));
      }
      syncFromSelect();
    });
  }

  // Sync on boot in case the page loads with a non-default system
  // already selected (e.g. via stored preference).
  syncFromSelect();
})();

// ─── P54-02: dock view-group → canvas switcher ────────────────────
//
// The top half of the dock holds 4 buttons (`data-view-target=...`)
// that switch which canvas-view paints in the main area. We mirror
// the tool-drawer pattern: clicking a view button sets
// `body[data-active-view="X"]` and CSS does the show/hide. Default
// view is "circuit" so the page boots with the control circuit
// already painted.
(function _wbViewSwitchBoot() {
  if (typeof document === "undefined") return;
  const dock = document.getElementById("workbench-dock");
  if (!dock) return;
  const buttons = Array.from(dock.querySelectorAll("[data-view-target]"));
  if (buttons.length === 0) return;

  // Boot default view if none is set yet.
  if (!document.body.dataset.activeView) {
    document.body.dataset.activeView = "circuit";
  }

  function setActiveView(view) {
    document.body.dataset.activeView = view || "circuit";
    for (const btn of buttons) {
      const isActive = btn.getAttribute("data-view-target") === view;
      btn.setAttribute("aria-pressed", isActive ? "true" : "false");
    }
  }

  // Sync aria-pressed with the boot default.
  setActiveView(document.body.dataset.activeView || "circuit");

  for (const btn of buttons) {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-view-target");
      if (target) setActiveView(target);
    });
  }
})();

// ─── JER-158: editable sandbox canvas shell ───────────────────────
//
// This is client-side draft scaffolding only. It lets engineers derive
// a sandbox candidate from the reference sample, select graph nodes,
// edit draft labels/ops, and inspect read-only evidence metadata. It
// never writes controller truth or promotes a candidate to certified.
function installEditableWorkbenchShell() {
  const shell = document.getElementById("workbench-editable-shell");
  if (!shell) return;

  let nodes = Array.from(shell.querySelectorAll("[data-editable-node-id]"));
  const canvas = document.getElementById("workbench-editable-canvas");
  const edgeSvg = shell.querySelector(".workbench-editable-edges");
  const toolbarButtons = Array.from(shell.querySelectorAll("[data-editor-tool]"));
  const viewportButtons = Array.from(shell.querySelectorAll("[data-viewport-tool]"));
  const opCatalogButtons = Array.from(shell.querySelectorAll("[data-op-catalog-op]"));
  const opCatalogStatus = document.getElementById("workbench-op-catalog-status");
  const componentLibraryButtons = Array.from(shell.querySelectorAll("[data-component-template-id]"));
  const componentLibraryStatus = document.getElementById("workbench-component-library-status");
  const captureSubsystemTemplateBtn = document.getElementById("workbench-capture-subsystem-template-btn");
  const insertCapturedTemplateBtn = document.getElementById("workbench-insert-captured-template-btn");
  const startEmptyDraftBtn = document.getElementById("workbench-start-empty-draft-btn");
  const deriveBtn = document.getElementById("workbench-derive-draft-btn");
  const runSandboxBtn = document.getElementById("workbench-run-sandbox-btn");
  const draftLabel = document.getElementById("workbench-draft-status-label");
  const draftHashLabel = document.getElementById("workbench-draft-hash-label");
  const graphValidationStatus = document.getElementById("workbench-graph-validation-status");
  const nodeIdSlot = document.getElementById("workbench-inspector-node-id");
  const labelInput = document.getElementById("workbench-inspector-node-label");
  const opSelect = document.getElementById("workbench-inspector-node-op");
  const ruleCountSlot = document.getElementById("workbench-inspector-rule-count");
  const ruleParameterOwner = document.getElementById("workbench-rule-parameter-owner");
  const ruleNameInput = document.getElementById("workbench-rule-name");
  const ruleSourceSignalInput = document.getElementById("workbench-rule-source-signal");
  const ruleComparisonSelect = document.getElementById("workbench-rule-comparison");
  const ruleThresholdInput = document.getElementById("workbench-rule-threshold");
  const applyRuleParameterBtn = document.getElementById("workbench-apply-rule-parameter-btn");
  const ruleParameterStatus = document.getElementById("workbench-rule-parameter-status");
  const subsystemNameInput = document.getElementById("workbench-subsystem-name");
  const subsystemOwner = document.getElementById("workbench-subsystem-owner");
  const createSubsystemBtn = document.getElementById("workbench-create-subsystem-btn");
  const renameSubsystemBtn = document.getElementById("workbench-rename-subsystem-btn");
  const ungroupSubsystemBtn = document.getElementById("workbench-ungroup-subsystem-btn");
  const subsystemStatus = document.getElementById("workbench-subsystem-status");
  const subsystemInterfaceOwner = document.getElementById("workbench-subsystem-interface-owner");
  const subsystemInterfaceDirectionSelect = document.getElementById("workbench-subsystem-interface-direction");
  const subsystemInterfaceLabelInput = document.getElementById("workbench-subsystem-interface-label");
  const subsystemInterfaceSignalInput = document.getElementById("workbench-subsystem-interface-signal-id");
  const subsystemInterfaceValueTypeSelect = document.getElementById("workbench-subsystem-interface-value-type");
  const subsystemInterfaceEvidenceStatusSelect = document.getElementById("workbench-subsystem-interface-evidence-status");
  const addSubsystemInterfacePortBtn = document.getElementById("workbench-add-subsystem-interface-port-btn");
  const removeSubsystemInterfacePortBtn = document.getElementById("workbench-remove-subsystem-interface-port-btn");
  const subsystemInterfaceContractList = document.getElementById("workbench-subsystem-interface-contract-list");
  const subsystemInterfaceStatus = document.getElementById("workbench-subsystem-interface-status");
  const evidenceSlot = document.getElementById("workbench-inspector-evidence-status");
  const signalCountSlot = document.getElementById("workbench-inspector-signal-count");
  const sourceRefSlot = document.getElementById("workbench-inspector-source-ref");
  const evidenceSummary = document.getElementById("workbench-inspector-evidence-summary");
  const evidenceDetail = document.getElementById("workbench-inspector-evidence-detail");
  const hardwareEvidenceV2Status = document.getElementById("workbench-hardware-evidence-v2-status");
  const hardwareEvidenceV2Target = document.getElementById("workbench-hardware-evidence-v2-target");
  const hardwareEvidenceV2Coverage = document.getElementById("workbench-hardware-evidence-v2-coverage");
  const hardwareEvidenceV2GapCount = document.getElementById("workbench-hardware-evidence-v2-gap-count");
  const hardwareEvidenceV2PinRows = document.getElementById("workbench-hardware-evidence-v2-pin-rows");
  const hardwareEvidenceV2Fields = document.getElementById("workbench-hardware-evidence-v2-fields");
  const hardwarePaletteFilter = document.getElementById("workbench-hardware-palette-filter");
  const hardwarePaletteAction = document.getElementById("workbench-hardware-palette-action");
  const hardwarePaletteList = document.getElementById("workbench-hardware-palette-list");
  const hardwarePaletteCount = document.getElementById("workbench-hardware-palette-count");
  const hardwarePaletteStatus = document.getElementById("workbench-hardware-palette-status");
  const diffPanel = document.getElementById("workbench-sandbox-diff-panel");
  const diffVerdict = document.getElementById("workbench-diff-verdict");
  const diffScenario = document.getElementById("workbench-diff-scenario");
  const diffModelHash = document.getElementById("workbench-diff-model-hash");
  const diffFirstDivergence = document.getElementById("workbench-diff-first-divergence");
  const workspaceDocumentRevisionSlot = document.getElementById("workbench-workspace-document-revision");
  const workspaceDocumentActionCountSlot = document.getElementById("workbench-workspace-document-action-count");
  const workspaceDocumentUndoDepthSlot = document.getElementById("workbench-workspace-document-undo-depth");
  const workspaceDocumentRedoDepthSlot = document.getElementById("workbench-workspace-document-redo-depth");
  const canvasSelectedNodeCountSlot = document.getElementById("workbench-canvas-selected-node-count");
  const canvasSelectedEdgeCountSlot = document.getElementById("workbench-canvas-selected-edge-count");
  const canvasLastActionSlot = document.getElementById("workbench-canvas-last-action");
  const diffReviewV2Panel = document.getElementById("workbench-diff-review-v2");
  const diffReviewV2Status = document.getElementById("workbench-diff-review-v2-status");
  const diffReviewV2Target = document.getElementById("workbench-diff-review-v2-target");
  const diffReviewV2Scenario = document.getElementById("workbench-diff-review-v2-scenario");
  const diffReviewV2Readiness = document.getElementById("workbench-diff-review-v2-readiness");
  const diffReviewV2ArchiveState = document.getElementById("workbench-diff-review-v2-archive-state");
  const diffReviewV2Divergence = document.getElementById("workbench-diff-review-v2-divergence");
  const diffReviewV2Claim = document.getElementById("workbench-diff-review-v2-claim");
  const sandboxTestBenchPanel = document.getElementById("workbench-sandbox-test-bench");
  const sandboxTestBenchInputs = document.getElementById("workbench-test-bench-inputs-json");
  const sandboxTestBenchAssertions = document.getElementById("workbench-test-bench-assertions-json");
  const runTestBenchBtn = document.getElementById("workbench-run-test-bench-btn");
  const sandboxTestBenchStatus = document.getElementById("workbench-test-bench-status");
  const sandboxTestBenchReportOutput = document.getElementById("workbench-test-bench-report-output");
  const candidateDebuggerPanel = document.getElementById("workbench-candidate-debugger-view");
  const candidateDebuggerStatus = document.getElementById("workbench-candidate-debugger-status");
  const candidateDebuggerTarget = document.getElementById("workbench-candidate-debugger-target");
  const candidateDebuggerTick = document.getElementById("workbench-candidate-debugger-tick");
  const candidateDebuggerAssertion = document.getElementById("workbench-candidate-debugger-assertion");
  const candidateDebuggerObserved = document.getElementById("workbench-candidate-debugger-observed");
  const candidateDebuggerTrace = document.getElementById("workbench-candidate-debugger-trace");
  const preflightPanel = document.getElementById("workbench-preflight-analyzer");
  const runPreflightBtn = document.getElementById("workbench-run-preflight-btn");
  const preflightClassification = document.getElementById("workbench-preflight-classification");
  const preflightFindingsCount = document.getElementById("workbench-preflight-findings-count");
  const preflightActions = document.getElementById("workbench-preflight-actions");
  const preflightOutput = document.getElementById("workbench-preflight-output");
  const timelineStrip = document.getElementById("workbench-sandbox-timeline-strip");
  const selectedDebugTimelineTarget = document.getElementById("workbench-selected-debug-target");
  const selectedDebugTimelineScenario = document.getElementById("workbench-selected-debug-scenario");
  const selectedDebugTimelineVerdict = document.getElementById("workbench-selected-debug-verdict");
  const selectedDebugTimelineLinkStatus = document.getElementById("workbench-selected-debug-link-status");
  const selectedDebugTimelineHardware = document.getElementById("workbench-selected-debug-hardware");
  const selectedDebugTimelineContext = document.getElementById("workbench-selected-debug-context");
  const handoffBtn = document.getElementById("workbench-generate-handoff-btn");
  const handoffStatus = document.getElementById("workbench-handoff-status");
  const linearHandoffOutput = document.getElementById("workbench-linear-handoff-output");
  const prProofOutput = document.getElementById("workbench-pr-proof-output");
  const changeRequestPacketOutput = document.getElementById("workbench-changerequest-packet-output");
  const prepareArchiveBtn = document.getElementById("workbench-prepare-archive-btn");
  const downloadArchiveBtn = document.getElementById("workbench-download-archive-btn");
  const archiveOutput = document.getElementById("workbench-evidence-archive-output");
  const archiveStatus = document.getElementById("workbench-archive-status");
  const interfaceBindingOwner = document.getElementById("workbench-interface-binding-owner");
  const interfaceHardwareIdInput = document.getElementById("workbench-interface-hardware-id");
  const interfaceCableInput = document.getElementById("workbench-interface-cable");
  const interfaceConnectorInput = document.getElementById("workbench-interface-connector");
  const interfacePortLocalInput = document.getElementById("workbench-interface-port-local");
  const interfacePortPeerInput = document.getElementById("workbench-interface-port-peer");
  const interfaceEvidenceStatusSelect = document.getElementById("workbench-interface-evidence-status");
  const applyInterfaceBindingBtn = document.getElementById("workbench-apply-interface-binding-btn");
  const interfaceBindingStatus = document.getElementById("workbench-interface-binding-status");
  const interfaceBindingQuality = document.getElementById("workbench-interface-binding-quality");
  const interfaceBindingCoverage = document.getElementById("workbench-interface-binding-coverage");
  const exportConnectorPinMapBtn = document.getElementById("workbench-export-connector-pin-map-btn");
  const applyConnectorPinMapBtn = document.getElementById("workbench-apply-connector-pin-map-btn");
  const connectorPinMapOutput = document.getElementById("workbench-connector-pin-map-output");
  const connectorPinMapStatus = document.getElementById("workbench-connector-pin-map-status");
  const exportHardwareInterfaceDesignBtn = document.getElementById("workbench-export-hardware-interface-design-btn");
  const validateHardwareInterfaceDesignBtn = document.getElementById("workbench-validate-hardware-interface-design-btn");
  const applyHardwareInterfaceDesignBtn = document.getElementById("workbench-apply-hardware-interface-design-btn");
  const hardwareInterfaceDesignOutput = document.getElementById("workbench-hardware-interface-design-output");
  const hardwareInterfaceDesignValidationOutput = document.getElementById("workbench-hardware-interface-design-validation-output");
  const hardwareInterfaceDesignStatus = document.getElementById("workbench-hardware-interface-design-status");
  const hardwareBindingDiagnosticsStatus = document.getElementById("workbench-hardware-binding-diagnostics-status");
  const hardwareBindingDiagnosticsCount = document.getElementById("workbench-hardware-binding-diagnostics-count");
  const hardwareBindingDiagnosticsGapCount = document.getElementById("workbench-hardware-binding-diagnostics-gap-count");
  const hardwareBindingDiagnosticsList = document.getElementById("workbench-hardware-binding-diagnostics-list");
  const exportInterfaceMatrixBtn = document.getElementById("workbench-export-interface-matrix-btn");
  const validateInterfaceMatrixBtn = document.getElementById("workbench-validate-interface-matrix-btn");
  const applyInterfaceMatrixBtn = document.getElementById("workbench-apply-interface-matrix-btn");
  const exportInterfaceMatrixCsvBtn = document.getElementById("workbench-export-interface-matrix-csv-btn");
  const importInterfaceMatrixCsvBtn = document.getElementById("workbench-import-interface-matrix-csv-btn");
  const interfaceMatrixOutput = document.getElementById("workbench-interface-matrix-output");
  const interfaceMatrixCsvOutput = document.getElementById("workbench-interface-matrix-csv-output");
  const interfaceMatrixStatus = document.getElementById("workbench-interface-matrix-status");
  const interfaceMatrixReview = document.getElementById("workbench-interface-matrix-review");
  const interfaceMatrixValidationOutput = document.getElementById("workbench-interface-matrix-validation-output");
  const typedPortOwner = document.getElementById("workbench-typed-port-owner");
  const portInputSignalInput = document.getElementById("workbench-port-input-signal");
  const portOutputSignalInput = document.getElementById("workbench-port-output-signal");
  const portValueTypeSelect = document.getElementById("workbench-port-value-type");
  const portUnitInput = document.getElementById("workbench-port-unit");
  const portRequiredInput = document.getElementById("workbench-port-required");
  const edgeSignalIdInput = document.getElementById("workbench-edge-signal-id");
  const edgeSourcePortInput = document.getElementById("workbench-edge-source-port");
  const edgeTargetPortInput = document.getElementById("workbench-edge-target-port");
  const applyPortContractBtn = document.getElementById("workbench-apply-port-contract-btn");
  const portContractStatus = document.getElementById("workbench-port-contract-status");
  const exportDraftBtn = document.getElementById("workbench-export-draft-btn");
  const importDraftBtn = document.getElementById("workbench-import-draft-btn");
  const draftJsonBuffer = document.getElementById("workbench-draft-json-buffer");
  const draftJsonStatus = document.getElementById("workbench-draft-json-status");
  const draftSnapshotNameInput = document.getElementById("workbench-draft-snapshot-name");
  const draftSnapshotSelect = document.getElementById("workbench-draft-snapshot-select");
  const saveDraftSnapshotBtn = document.getElementById("workbench-save-draft-snapshot-btn");
  const restoreDraftSnapshotBtn = document.getElementById("workbench-restore-draft-snapshot-btn");
  const deleteDraftSnapshotBtn = document.getElementById("workbench-delete-draft-snapshot-btn");
  const draftSnapshotStatus = document.getElementById("workbench-draft-snapshot-status");
  const scenarioSelect = document.getElementById("workbench-sandbox-scenario-select");
  const customSnapshotInput = document.getElementById("workbench-custom-snapshot-json");
  const storageKey = "well-harness-editable-workbench-draft-v1";
  const snapshotsStorageKey = "well-harness-editable-workbench-draft-snapshots-v1";
  let selectedNode = nodes.find((node) => node.getAttribute("aria-pressed") === "true") || nodes[0];
  let selectedNodeIds = new Set(selectedNode ? [selectedNode.getAttribute("data-editable-node-id") || ""] : []);
  let selectedEdge = null;
  let lassoDragState = null;
  let groupDragState = null;
  let selectionMarquee = null;
  let suppressNextNodeClick = false;
  let pendingPortHandleSource = null;
  let viewportPanState = null;
  let spacePanActive = false;
  let hardwareEvidenceReport = null;
  let hardwarePaletteItems = [];
  let selectedHardwarePaletteItemId = "";
  let lastSandboxDiff = null;
  let selectedDiagnosticFocus = null;
  let repairActionLog = [];
  let lastInterfaceMatrixValidationReport = null;
  let currentEditorTool = "select";
  let pendingEdgeSourceId = "";
  let nextDraftNodeIndex = 1;
  let selectedCatalogOp = "and";
  let lastComponentTemplateId = "";
  let capturedSubsystemTemplates = [];
  let lastSandboxTestRunReport = null;
  let nextCapturedSubsystemTemplateIndex = 1;
  let nextSubsystemGroupIndex = 1;
  let subsystemGroups = [];
  let lastPreflightAnalyzerReport = null;
  let lastHardwareInterfaceDesignerPayload = null;
  let lastHardwareInterfaceDesignerValidationReport = null;
  let canvasAuthoringMode = "reference_sample";
  const workspaceDocumentKind = "well-harness-workbench-workspace-document";
  const workspaceDocumentVersion = "workbench-workspace-document.v1";
  let workspaceDocumentId = "ui_draft_workspace_document_v1";
  let workspaceDocumentRevision = "ui_draft_pending";
  let workspaceDocumentParentRevision = null;
  let workspaceActionLog = [];
  const canvasInteractionSummaryKind = "well-harness-workbench-canvas-interaction-summary";
  const canvasInteractionSummaryVersion = "workbench-canvas-interaction-summary.v1";
  let lastCanvasInteractionAction = "init";
  const editableGraphDocumentKind = "well-harness-workbench-editable-graph-document";
  const editableGraphDocumentVersionV1 = "workbench-editable-graph-document.v1";
  const editableGraphDocumentVersion = "workbench-editable-graph-document.v2";
  const editableGraphDocumentAcceptedImportVersions = [
    editableGraphDocumentVersionV1,
    editableGraphDocumentVersion,
  ];
  const editableGraphCanonicalModelVersion = "workbench-editable-graph-canonical-model.v1";
  const editableGraphDomAdapterBoundaryVersion =
    "workbench-editable-graph-dom-adapter-boundary.v1";
  const sandboxTestBenchKind = "well-harness-workbench-sandbox-test-bench";
  const sandboxTestBenchVersion = "workbench-sandbox-test-bench.v1";
  const sandboxTestRunReportKind = "well-harness-workbench-sandbox-test-run-report";
  const sandboxTestRunReportVersion = "workbench-sandbox-test-run-report.v1";
  const candidateDebuggerViewKind = "well-harness-workbench-candidate-debugger-view";
  const candidateDebuggerViewVersion = "workbench-candidate-debugger-view.v1";
  const preflightAnalyzerReportKind = "well-harness-workbench-preflight-analyzer-report";
  const preflightAnalyzerReportVersion = "workbench-preflight-analyzer.v1";
  const hardwareInterfaceDesignerSchemaId =
    "https://well-harness.local/json_schema/editable_hardware_interface_design_v1.schema.json";
  const hardwareInterfaceDesignerKind = "well-harness-editable-hardware-interface-design";
  const hardwareInterfaceDesignerVersion = 1;
  const hardwareInterfaceDesignerValidationKind =
    "well-harness-workbench-hardware-interface-designer-validation-report";
  const hardwareInterfaceDesignerValidationVersion =
    "workbench-hardware-interface-designer-validation.v1";
  const edgeRouteMetadataVersion = "workbench-edge-route-metadata.v1";
  let draftEdges = [
    { id: "edge_logic1_logic2", source: "logic1", target: "logic2" },
    { id: "edge_logic2_logic3", source: "logic2", target: "logic3" },
    { id: "edge_logic3_logic4", source: "logic3", target: "logic4" },
  ];
  const undoStack = [];
  const redoStack = [];
  const viewportState = {
    scale: 1,
    panX: 0,
    panY: 0,
  };
  const viewportScaleBounds = {
    min: 0.35,
    max: 2.6,
  };
  const interfaceBindingRequiredFields = [
    "hardware_id",
    "cable",
    "connector",
    "port_local",
    "port_peer",
  ];
  const approvedRuleComparisons = [
    "==",
    "!=",
    "<",
    "<=",
    ">",
    ">=",
    "between_lower_inclusive",
    "between_exclusive",
  ];
  const editableOperationCatalogVersion = "editable-control-ops.v1";
  const approvedOperationCatalog = {
    "input": {
      op: "input",
      label: "Input primitive",
      short_label: "IN",
      value_type: "boolean",
      rule_count: "0",
    },
    "output": {
      op: "output",
      label: "Output primitive",
      short_label: "OUT",
      value_type: "boolean",
      rule_count: "0",
    },
    and: {
      op: "and",
      label: "AND gate",
      short_label: "AND",
      value_type: "boolean",
      rule_count: "2",
    },
    or: {
      op: "or",
      label: "OR gate",
      short_label: "OR",
      value_type: "boolean",
      rule_count: "2",
    },
    compare: {
      op: "compare",
      label: "Compare threshold",
      short_label: "CMP",
      value_type: "number",
      rule_count: "1",
    },
    between: {
      op: "between",
      label: "Between window",
      short_label: "BTW",
      value_type: "number",
      rule_count: "2",
    },
    delay: {
      op: "delay",
      label: "Delay block",
      short_label: "DLY",
      value_type: "boolean",
      rule_count: "1",
    },
    latch: {
      op: "latch",
      label: "Latch block",
      short_label: "LAT",
      value_type: "boolean",
      rule_count: "1",
    },
  };
  const componentLibraryVersion = "editable-component-library.v1";
  const capturedSubsystemTemplateVersion = "editable-captured-subsystem-template.v1";
  const componentLibraryTemplates = {
    single_and_gate: {
      id: "single_and_gate",
      label: "Single AND",
      short_label: "AND",
      nodes: [
        { label: "Reusable AND gate", op: "and", rule_count: "2", x_offset: 0, y_offset: 0 },
      ],
      edges: [],
    },
    compare_guard: {
      id: "compare_guard",
      label: "Compare guard",
      short_label: "CMP",
      nodes: [
        { label: "Reusable compare guard", op: "compare", rule_count: "1", x_offset: 0, y_offset: 0 },
      ],
      edges: [],
    },
    two_stage_interlock: {
      id: "two_stage_interlock",
      label: "Two-stage interlock",
      short_label: "2ST",
      nodes: [
        { label: "Interlock input gate", op: "and", rule_count: "2", x_offset: -5, y_offset: -4 },
        { label: "Interlock compare guard", op: "compare", rule_count: "1", x_offset: 11, y_offset: 8 },
      ],
      edges: [
        { source_index: 0, target_index: 1, value_type: "boolean", required: true },
      ],
    },
  };

  function operationCatalogEntry(op) {
    return approvedOperationCatalog[op] || approvedOperationCatalog.and;
  }

  function buildOperationCatalogSummary() {
    return {
      version: editableOperationCatalogVersion,
      approved_ops: Object.keys(approvedOperationCatalog),
      selected_op: selectedCatalogOp,
      truth_effect: "none",
    };
  }

  function normalizeCanvasAuthoringMode(value) {
    const mode = String(value || "").trim();
    return mode === "empty_authoring" ? "empty_authoring" : "reference_sample";
  }

  function componentTemplateById(templateId) {
    const id = String(templateId || "").trim();
    return componentLibraryTemplates[id] || capturedSubsystemTemplates.find((template) => template.id === id) || null;
  }

  function componentTemplateIds() {
    return [
      ...Object.keys(componentLibraryTemplates),
      ...capturedSubsystemTemplates.map((template) => template.id),
    ].sort();
  }

  function capturedSubsystemTemplateSnapshot() {
    return capturedSubsystemTemplates.map((template) => cloneJson(template));
  }

  function buildComponentLibrarySummary() {
    const capturedTemplates = capturedSubsystemTemplateSnapshot();
    return {
      version: componentLibraryVersion,
      template_ids: componentTemplateIds(),
      template_count: componentTemplateIds().length,
      last_template_id: lastComponentTemplateId || null,
      captured_template_version: capturedSubsystemTemplateVersion,
      captured_template_ids: capturedTemplates.map((template) => template.id),
      captured_template_count: capturedTemplates.length,
      last_captured_template_id: capturedTemplates.length
        ? capturedTemplates[capturedTemplates.length - 1].id
        : null,
      captured_templates: capturedTemplates,
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    };
  }

  function refreshCapturedSubsystemTemplateControls() {
    if (insertCapturedTemplateBtn) {
      insertCapturedTemplateBtn.disabled = capturedSubsystemTemplates.length === 0;
    }
    if (captureSubsystemTemplateBtn) {
      captureSubsystemTemplateBtn.disabled = false;
    }
  }

  function normalizeCapturedTemplateLabel(value, fallbackIndex) {
    const text = String(value === null || value === undefined ? "" : value).trim();
    return text || `Captured subsystem ${fallbackIndex || 1}`;
  }

  function normalizeCapturedTemplateNodeRecord(record, fallbackIndex) {
    if (!record || typeof record !== "object" || Array.isArray(record)) return null;
    const op = operationCatalogEntry(record.op || record.op_catalog_entry || record.opCatalogEntry || "and").op;
    return {
      original_node_id: String(record.original_node_id || record.originalNodeId || record.id || "").trim(),
      label: String(record.label || `Captured node ${fallbackIndex || 1}`),
      op,
      rule_count: String(record.rule_count || record.ruleCount || operationCatalogEntry(op).rule_count || "0"),
      evidence: String(record.evidence || "evidence_gap"),
      source_ref: String(record.source_ref || record.sourceRef || "ui_draft.component_library.capture.node"),
      op_catalog_entry: op,
      hardware_binding: normalizeInterfaceBinding(
        record.hardware_binding || record.hardwareBinding || {},
        "node_template",
        String(record.original_node_id || record.originalNodeId || record.id || fallbackIndex || "unknown"),
      ),
      port_contract: record.port_contract || record.portContract || null,
      rules: Array.isArray(record.rules) ? cloneJson(record.rules) : [],
      x_offset: Number.parseFloat(record.x_offset || record.xOffset || "0") || 0,
      y_offset: Number.parseFloat(record.y_offset || record.yOffset || "0") || 0,
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    };
  }

  function normalizeCapturedTemplateEdgeRecord(record, fallbackIndex) {
    if (!record || typeof record !== "object" || Array.isArray(record)) return null;
    return {
      original_edge_id: String(record.original_edge_id || record.originalEdgeId || record.id || "").trim(),
      source_index: Number.parseInt(record.source_index || record.sourceIndex || "0", 10) || 0,
      target_index: Number.parseInt(record.target_index || record.targetIndex || "0", 10) || 0,
      source_port_id: record.source_port_id ? String(record.source_port_id) : undefined,
      target_port_id: record.target_port_id ? String(record.target_port_id) : undefined,
      signal_id: record.signal_id ? String(record.signal_id) : undefined,
      value_type: normalizePortValueType(record.value_type || record.valueType || "boolean"),
      unit: String(record.unit || ""),
      required: normalizePortRequired(record.required),
      source_ref: String(record.source_ref || record.sourceRef || `ui_draft.component_library.capture.edge.${fallbackIndex || 1}`),
      hardware_binding: normalizeInterfaceBinding(
        record.hardware_binding || record.hardwareBinding || {},
        "edge_template",
        String(record.original_edge_id || record.originalEdgeId || record.id || fallbackIndex || "unknown"),
      ),
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    };
  }

  function normalizeCapturedSubsystemTemplateRecord(record, fallbackIndex) {
    if (!record || typeof record !== "object" || Array.isArray(record)) return null;
    const id = String(record.id || `captured_subsystem_template_${fallbackIndex || 1}`).trim();
    if (!id) return null;
    const nodes = (Array.isArray(record.nodes) ? record.nodes : [])
      .map((node, index) => normalizeCapturedTemplateNodeRecord(node, index + 1))
      .filter(Boolean);
    const edges = (Array.isArray(record.edges) ? record.edges : [])
      .map((edge, index) => normalizeCapturedTemplateEdgeRecord(edge, index + 1))
      .filter((edge) => edge && edge.source_index >= 0 && edge.target_index >= 0);
    const subsystem = normalizeSubsystemGroupRecord(
      record.subsystem || record.subsystem_group || record.subsystemGroup || {
        id: `captured_subsystem_${fallbackIndex || 1}`,
        name: record.label,
        node_ids: nodes.map((node) => node.original_node_id).filter(Boolean),
      },
      fallbackIndex || 1,
    ) || {
      id: `captured_subsystem_${fallbackIndex || 1}`,
      name: normalizeCapturedTemplateLabel(record.label, fallbackIndex),
      node_ids: nodes.map((node) => node.original_node_id).filter(Boolean),
      candidate_state: "sandbox_candidate",
      source_ref: `ui_draft.component_library.${id}.subsystem`,
      truth_effect: "none",
    };
    const normalized = {
      id,
      kind: "well-harness-workbench-captured-subsystem-template",
      version: 1,
      template_version: capturedSubsystemTemplateVersion,
      label: normalizeCapturedTemplateLabel(record.label || subsystem.name, fallbackIndex),
      short_label: String(record.short_label || record.shortLabel || "CAP").slice(0, 4).toUpperCase() || "CAP",
      captured_at: String(record.captured_at || record.capturedAt || "browser_local_draft"),
      capture_source: String(record.capture_source || record.captureSource || "ui_draft.component_library.capture"),
      subsystem,
      nodes,
      edges,
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_effect: "none",
    };
    return {
      ...normalized,
      checksum: editableDraftHash(stableEvidenceArchiveJson(normalized)),
    };
  }

  function normalizeCapturedSubsystemTemplates(records) {
    const normalized = [];
    const usedIds = new Set();
    for (const record of Array.isArray(records) ? records : []) {
      const template = normalizeCapturedSubsystemTemplateRecord(record, normalized.length + 1);
      if (!template || usedIds.has(template.id)) continue;
      usedIds.add(template.id);
      normalized.push(template);
    }
    nextCapturedSubsystemTemplateIndex = 1;
    while (usedIds.has(`captured_subsystem_template_${nextCapturedSubsystemTemplateIndex}`)) {
      nextCapturedSubsystemTemplateIndex += 1;
    }
    return normalized;
  }

  function nextCapturedSubsystemTemplateId() {
    const usedIds = new Set(capturedSubsystemTemplates.map((template) => template.id));
    while (usedIds.has(`captured_subsystem_template_${nextCapturedSubsystemTemplateIndex}`)) {
      nextCapturedSubsystemTemplateIndex += 1;
    }
    const templateId = `captured_subsystem_template_${nextCapturedSubsystemTemplateIndex}`;
    nextCapturedSubsystemTemplateIndex += 1;
    return templateId;
  }

  function remapTemplateValue(value, idMap) {
    if (typeof value === "string") {
      let remapped = value;
      const remapEntries = Object.entries(idMap || {})
        .filter(([sourceId, targetId]) => sourceId && targetId)
        .sort(([left], [right]) => right.length - left.length);
      const placeholders = remapEntries.map((_, index) => `__WB_TEMPLATE_REMAP_${index}__`);
      remapEntries.forEach(([sourceId], index) => {
        remapped = remapped.split(sourceId).join(placeholders[index]);
      });
      remapEntries.forEach(([, targetId], index) => {
        remapped = remapped.split(placeholders[index]).join(targetId);
      });
      for (const placeholder of placeholders) {
        if (remapped.includes(placeholder)) {
          remapped = remapped.split(placeholder).join("");
        }
      }
      return remapped;
    }
    if (Array.isArray(value)) {
      return value.map((item) => remapTemplateValue(item, idMap));
    }
    if (value && typeof value === "object") {
      return Object.fromEntries(
        Object.entries(value).map(([key, item]) => [key, remapTemplateValue(item, idMap)]),
      );
    }
    return value;
  }

  function setSelectedOperationCatalogEntry(op) {
    const entry = operationCatalogEntry(op);
    selectedCatalogOp = entry.op;
    for (const button of opCatalogButtons) {
      button.setAttribute(
        "aria-pressed",
        button.getAttribute("data-op-catalog-op") === selectedCatalogOp ? "true" : "false",
      );
    }
    if (opCatalogStatus) {
      opCatalogStatus.textContent = `${entry.short_label} · ${entry.value_type}`;
    }
    return entry;
  }

  function normalizedInterfaceField(value) {
    const text = String(value === null || value === undefined ? "" : value).trim();
    return text || "evidence_gap";
  }

  function isInterfaceEvidenceGap(value) {
    return !value || value === "evidence_gap";
  }

  function normalizeEvidenceStatus(value) {
    const status = normalizedInterfaceField(value);
    return ["evidence_gap", "ui_draft", "not_recorded"].includes(status)
      ? status
      : "evidence_gap";
  }

  function interfaceBindingQualityReport(binding) {
    const source = binding && typeof binding === "object" ? binding : {};
    const missingFields = interfaceBindingRequiredFields
      .filter((fieldName) => isInterfaceEvidenceGap(source[fieldName]));
    if (source.evidence_status !== "ui_draft") {
      missingFields.push("evidence_status");
    }
    const completeFields = interfaceBindingRequiredFields.length
      - missingFields.filter((fieldName) => fieldName !== "evidence_status").length;
    const hasAnyField = interfaceBindingRequiredFields
      .some((fieldName) => !isInterfaceEvidenceGap(source[fieldName]));
    const status = !hasAnyField && source.evidence_status !== "ui_draft"
      ? "missing"
      : (missingFields.length ? "partial" : "complete");
    return {
      status,
      label: `HW ${status}`,
      required_fields: [...interfaceBindingRequiredFields, "evidence_status"],
      missing_fields: missingFields,
      complete_fields: completeFields,
      truth_effect: "none",
    };
  }

  function bindQualityToInterfaceBinding(binding) {
    const quality = interfaceBindingQualityReport(binding);
    return {
      ...binding,
      binding_quality: quality.status,
      binding_quality_label: quality.label,
      binding_missing_fields: quality.missing_fields,
      binding_required_fields: quality.required_fields,
      binding_complete_fields: quality.complete_fields,
    };
  }

  function normalizeInterfaceBinding(binding, ownerKind, ownerId) {
    const source = binding && typeof binding === "object" ? binding : {};
    const normalizedOwnerKind = ownerKind || normalizedInterfaceField(source.owner_kind || source.ownerKind);
    const normalizedOwnerId = ownerId || normalizedInterfaceField(source.owner_id || source.ownerId);
    return bindQualityToInterfaceBinding({
      id: normalizedInterfaceField(source.id || `ui-interface-binding:${normalizedOwnerKind}:${normalizedOwnerId}`),
      owner_kind: normalizedOwnerKind,
      owner_id: normalizedOwnerId,
      hardware_id: normalizedInterfaceField(source.hardware_id || source.hardwareId),
      cable: normalizedInterfaceField(source.cable),
      connector: normalizedInterfaceField(source.connector),
      port_local: normalizedInterfaceField(source.port_local || source.portLocal),
      port_peer: normalizedInterfaceField(source.port_peer || source.portPeer),
      pin_local: normalizedInterfaceField(source.pin_local || source.pinLocal),
      pin_peer: normalizedInterfaceField(source.pin_peer || source.pinPeer),
      evidence_status: normalizeEvidenceStatus(source.evidence_status || source.evidenceStatus),
      binding_kind: "ui_interface_binding",
      source_ref: normalizedInterfaceField(source.source_ref || source.sourceRef || "ui_draft.interface_binding"),
      truth_effect: "none",
    });
  }

  function applyNodeBindingQuality(node, binding) {
    if (!node) return;
    const quality = interfaceBindingQualityReport(binding);
    node.setAttribute("data-binding-quality", quality.status);
    node.setAttribute("data-binding-quality-label", quality.label);
  }

  function setNodeInterfaceBinding(node, binding) {
    if (!node) return null;
    const ownerId = node.getAttribute("data-editable-node-id") || "";
    const normalized = normalizeInterfaceBinding(binding, "node", ownerId);
    node.setAttribute("data-interface-hardware-id", normalized.hardware_id);
    node.setAttribute("data-interface-cable", normalized.cable);
    node.setAttribute("data-interface-connector", normalized.connector);
    node.setAttribute("data-interface-port-local", normalized.port_local);
    node.setAttribute("data-interface-port-peer", normalized.port_peer);
    node.setAttribute("data-interface-pin-local", normalized.pin_local);
    node.setAttribute("data-interface-pin-peer", normalized.pin_peer);
    node.setAttribute("data-interface-evidence-status", normalized.evidence_status);
    node.setAttribute("data-interface-source-ref", normalized.source_ref);
    applyNodeBindingQuality(node, normalized);
    return normalized;
  }

  function nodeInterfaceBinding(node) {
    if (!node) return normalizeInterfaceBinding({}, "node", "unknown");
    return normalizeInterfaceBinding({
      hardware_id: node.getAttribute("data-interface-hardware-id"),
      cable: node.getAttribute("data-interface-cable"),
      connector: node.getAttribute("data-interface-connector"),
      port_local: node.getAttribute("data-interface-port-local"),
      port_peer: node.getAttribute("data-interface-port-peer"),
      pin_local: node.getAttribute("data-interface-pin-local"),
      pin_peer: node.getAttribute("data-interface-pin-peer"),
      evidence_status: node.getAttribute("data-interface-evidence-status"),
      source_ref: node.getAttribute("data-interface-source-ref"),
    }, "node", node.getAttribute("data-editable-node-id") || "unknown");
  }

  function edgeInterfaceBinding(edge) {
    const edgeId = edge && (edge.id || `${edge.source || "unknown"}->${edge.target || "unknown"}`);
    return normalizeInterfaceBinding(
      edge && (edge.hardware_binding || edge.hardwareBinding || {}),
      "edge",
      edgeId || "unknown",
    );
  }

  function setEdgeInterfaceBinding(edge, binding) {
    if (!edge) return null;
    const normalized = normalizeInterfaceBinding(binding, "edge", edge.id || `${edge.source || "unknown"}->${edge.target || "unknown"}`);
    edge.hardware_binding = normalized;
    edge.binding_quality = normalized.binding_quality;
    return normalized;
  }

  function meaningfulInterfaceBinding(binding) {
    if (!binding || typeof binding !== "object") return false;
    return (
      binding.evidence_status === "ui_draft"
      || ["hardware_id", "cable", "connector", "port_local", "port_peer"]
        .concat(["pin_local", "pin_peer"])
        .some((key) => binding[key] && binding[key] !== "evidence_gap")
    );
  }

  function nodeBindingFocusTarget(node, nodeIndex) {
    const nodeId = editableNodeId(node) || "unknown";
    return {
      kind: "node",
      target_kind: "node",
      target_id: nodeId,
      node_id: nodeId,
      node_index: nodeIndex,
      owner_key: `node:${nodeId}`,
      focus_effect: "selection_only",
      truth_effect: "none",
    };
  }

  function edgeBindingFocusTarget(edge, edgeIndex) {
    const edgeId = edge && (edge.id || `${edge.source || "unknown"}->${edge.target || "unknown"}`);
    return {
      kind: "edge",
      target_kind: "edge",
      target_id: edgeId || "unknown",
      edge_id: edgeId || "unknown",
      edge_index: edgeIndex,
      source_node_id: edge && edge.source ? edge.source : "unknown",
      target_node_id: edge && edge.target ? edge.target : "unknown",
      signal_id: edge && edge.signal_id ? edge.signal_id : "evidence_gap",
      owner_key: `edge:${edgeId || "unknown"}`,
      focus_effect: "selection_only",
      truth_effect: "none",
    };
  }

  function collectWorkbenchHardwareBindings() {
    refreshEditableNodes();
    const nodeBindings = nodes.map((node, index) => ({
      ...nodeInterfaceBinding(node),
      focus_target: nodeBindingFocusTarget(node, index),
    }));
    const edgeBindings = draftEdges.map((edge, index) => ({
      ...edgeInterfaceBinding(edge),
      focus_target: edgeBindingFocusTarget(edge, index),
    }));
    return [...nodeBindings, ...edgeBindings].filter(meaningfulInterfaceBinding);
  }

  function connectorPinMapRowFromBinding(binding, index) {
    const normalized = normalizeInterfaceBinding(
      binding,
      binding && binding.owner_kind,
      binding && binding.owner_id,
    );
    return {
      row_id: `connector-pin:${String(index + 1).padStart(2, "0")}:${normalized.owner_kind}:${normalized.owner_id}`,
      owner_kind: normalized.owner_kind,
      owner_id: normalized.owner_id,
      hardware_id: normalized.hardware_id,
      cable: normalized.cable,
      connector: normalized.connector,
      port_local: normalized.port_local,
      port_peer: normalized.port_peer,
      pin_local: normalized.pin_local,
      pin_peer: normalized.pin_peer,
      signal_id: normalizedInterfaceField(normalized.signal_id || normalized.owner_id),
      evidence_status: normalized.evidence_status,
      source_ref: normalized.source_ref,
      truth_effect: "none",
    };
  }

  function buildWorkbenchConnectorPinMap(bindings) {
    const rows = (Array.isArray(bindings) ? bindings : [])
      .map((binding, index) => connectorPinMapRowFromBinding(binding, index));
    const evidenceGapFieldCount = rows.reduce((total, row) => (
      total + ["connector", "port_local", "port_peer", "pin_local", "pin_peer"]
        .filter((fieldName) => isInterfaceEvidenceGap(row[fieldName])).length
    ), 0);
    return {
      kind: "well-harness-workbench-connector-pin-map",
      version: 1,
      system_id: "thrust-reverser",
      map_scope: "sandbox_candidate_interface_design",
      row_count: rows.length,
      evidence_gap_field_count: evidenceGapFieldCount,
      rows,
      truth_effect: "none",
    };
  }

  function validateConnectorPinMapPayload(payload) {
    if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
      throw new Error("connector pin map JSON must be an object");
    }
    if (payload.kind !== "well-harness-workbench-connector-pin-map") {
      throw new Error("connector pin map kind must be well-harness-workbench-connector-pin-map");
    }
    if (payload.truth_effect !== "none") {
      throw new Error("connector pin map truth_effect must be none");
    }
    if (!Array.isArray(payload.rows)) {
      throw new Error("connector pin map rows must be an array");
    }
    for (const row of payload.rows) {
      if (!row || typeof row !== "object" || Array.isArray(row)) {
        throw new Error("connector pin map row must be an object");
      }
      if (row.truth_effect !== "none") {
        throw new Error("connector pin map row truth_effect must be none");
      }
    }
    return payload;
  }

  function connectorPinBindingFromRow(row) {
    const current = interfaceMatrixCurrentBinding(
      normalizedInterfaceField(row.owner_kind),
      normalizedInterfaceField(row.owner_id),
    ) || {};
    return normalizeInterfaceBinding({
      ...current,
      hardware_id: row.hardware_id,
      cable: row.cable,
      connector: row.connector,
      port_local: row.port_local,
      port_peer: row.port_peer,
      pin_local: row.pin_local,
      pin_peer: row.pin_peer,
      evidence_status: row.evidence_status,
      source_ref: row.source_ref || `ui_draft.connector_pin_map.${row.owner_kind || "unknown"}.${row.owner_id || "unknown"}`,
    }, row.owner_kind, row.owner_id);
  }

  function exportWorkbenchConnectorPinMap() {
    const map = buildWorkbenchConnectorPinMap(collectWorkbenchHardwareBindings());
    if (connectorPinMapOutput) {
      connectorPinMapOutput.value = JSON.stringify(map, null, 2);
    }
    if (connectorPinMapStatus) {
      connectorPinMapStatus.textContent =
        `Exported ${map.row_count || 0} connector/pin row(s), ${map.evidence_gap_field_count || 0} evidence-gap field(s). Truth effect: none.`;
    }
    return map;
  }

  function applyConnectorPinMapRows(rows) {
    let applied = 0;
    let skipped = 0;
    refreshEditableNodes();
    for (const row of rows || []) {
      const ownerKind = normalizedInterfaceField(row.owner_kind);
      const ownerId = normalizedInterfaceField(row.owner_id);
      const binding = connectorPinBindingFromRow(row);
      if (ownerKind === "node") {
        const node = nodes.find((candidate) => editableNodeId(candidate) === ownerId);
        if (!node) {
          skipped += 1;
          continue;
        }
        setNodeInterfaceBinding(node, binding);
        applied += 1;
        continue;
      }
      if (ownerKind === "edge") {
        const edge = draftEdges.find((candidate) => (
          candidate.id === ownerId
          || `${candidate.source || "unknown"}->${candidate.target || "unknown"}` === ownerId
        ));
        if (!edge) {
          skipped += 1;
          continue;
        }
        setEdgeInterfaceBinding(edge, binding);
        applied += 1;
        continue;
      }
      skipped += 1;
    }
    return { applied, skipped };
  }

  function applyWorkbenchConnectorPinMap() {
    if (!connectorPinMapOutput) return null;
    try {
      const payload = validateConnectorPinMapPayload(JSON.parse(connectorPinMapOutput.value || "{}"));
      if (payload.rows.length) {
        recordEditableHistory("connector_pin_map_apply");
        shell.setAttribute("data-draft-state", "derived");
      }
      const summary = applyConnectorPinMapRows(payload.rows);
      if (summary.applied > 0) {
        if (draftLabel) draftLabel.textContent = "sandbox_candidate connector/pin map applied";
        renderEditableEdges();
        renderInspector();
        validateEditableGraph();
        updateEditableDraftHash();
        persistDraft();
      }
      const refreshed = exportWorkbenchConnectorPinMap();
      if (connectorPinMapStatus) {
        connectorPinMapStatus.textContent =
          `Applied ${summary.applied} connector/pin row(s), skipped ${summary.skipped}. Export now has ${refreshed.row_count || 0} row(s). Truth effect: none.`;
      }
      return summary;
    } catch (err) {
      if (connectorPinMapStatus) {
        connectorPinMapStatus.textContent =
          err && err.message ? err.message : "connector pin map import failed";
      }
      return null;
    }
  }

  function emptyHardwareInterfaceDesignerPayload() {
    return {
      $schema: hardwareInterfaceDesignerSchemaId,
      kind: hardwareInterfaceDesignerKind,
      version: hardwareInterfaceDesignerVersion,
      design_id: "ui_draft_hardware_interface_design_v1",
      system_id: "thrust-reverser",
      candidate_state: "sandbox_candidate",
      truth_level_impact: "none",
      dal_pssa_impact: "none",
      controller_truth_modified: false,
      runtime_truth_effect: "none",
      lrus: [],
      cables: [],
      connectors: [],
      ports: [],
      pins: [],
      bindings: [],
      evidence_gaps: [],
      evidence_metadata: {
        sample_pack_role: "hardware_interface_design",
        source_refs: ["ui_draft.hardware_interface_designer"],
      },
      boundaries: {
        runtime_scope: "sandbox_only",
        hardware_truth_effect: "none",
        certified_truth_modified: false,
        dal_pssa_impact: "none",
      },
    };
  }

  function normalizeHardwareInterfaceDesignerArray(value) {
    return Array.isArray(value)
      ? value.filter((item) => item && typeof item === "object" && !Array.isArray(item)).map((item) => ({ ...item }))
      : [];
  }

  function normalizeHardwareInterfaceDesignerPayload(payload) {
    const defaults = emptyHardwareInterfaceDesignerPayload();
    const source = payload && typeof payload === "object" && !Array.isArray(payload) ? payload : {};
    return {
      ...defaults,
      ...source,
      evidence_metadata: {
        ...defaults.evidence_metadata,
        ...(source.evidence_metadata && typeof source.evidence_metadata === "object" && !Array.isArray(source.evidence_metadata)
          ? source.evidence_metadata
          : {}),
      },
      boundaries: {
        ...defaults.boundaries,
        ...(source.boundaries && typeof source.boundaries === "object" && !Array.isArray(source.boundaries)
          ? source.boundaries
          : {}),
      },
      lrus: normalizeHardwareInterfaceDesignerArray(source.lrus),
      cables: normalizeHardwareInterfaceDesignerArray(source.cables),
      connectors: normalizeHardwareInterfaceDesignerArray(source.connectors),
      ports: normalizeHardwareInterfaceDesignerArray(source.ports),
      pins: normalizeHardwareInterfaceDesignerArray(source.pins),
      bindings: normalizeHardwareInterfaceDesignerArray(source.bindings),
      evidence_gaps: normalizeHardwareInterfaceDesignerArray(source.evidence_gaps),
    };
  }

  function hardwareInterfaceDesignerFinding(code, severity, message, path, action) {
    return {
      code,
      severity,
      message,
      path: path || "",
      action: action || "Update sandbox hardware/interface design evidence before review.",
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_effect: "none",
    };
  }

  function hardwareInterfaceDesignerCollectionIds(payload) {
    const ids = {};
    for (const collection of ["lrus", "cables", "connectors", "ports", "pins", "bindings", "evidence_gaps"]) {
      ids[collection] = new Set((payload[collection] || []).map((item) => String(item.id || "")));
    }
    return ids;
  }

  function addHardwareInterfaceDesignerDuplicateFindings(payload, findings) {
    const seenGlobal = new Map();
    for (const collection of ["lrus", "cables", "connectors", "ports", "pins", "bindings", "evidence_gaps"]) {
      const seenLocal = new Map();
      for (const [index, item] of (payload[collection] || []).entries()) {
        const itemId = String(item.id || "").trim();
        if (!itemId) {
          findings.push(hardwareInterfaceDesignerFinding(
            "missing_hardware_interface_id",
            "error",
            `${collection}[${index}] is missing id.`,
            `${collection}.${index}.id`,
            "Add a stable sandbox id before applying.",
          ));
          continue;
        }
        if (seenLocal.has(itemId)) {
          findings.push(hardwareInterfaceDesignerFinding(
            "duplicate_hardware_interface_id",
            "error",
            `Duplicate id ${itemId} in ${collection}.`,
            `${collection}.${index}.id`,
            "Use one unique id per LRU, cable, connector, port, pin, binding, or evidence gap.",
          ));
        }
        seenLocal.set(itemId, collection);
        if (seenGlobal.has(itemId)) {
          findings.push(hardwareInterfaceDesignerFinding(
            "duplicate_hardware_interface_id",
            "error",
            `Duplicate id ${itemId} across ${seenGlobal.get(itemId)} and ${collection}.`,
            `${collection}.${index}.id`,
            "Keep hardware/interface ids globally unique inside the sandbox design.",
          ));
        } else {
          seenGlobal.set(itemId, collection);
        }
      }
    }
  }

  function addHardwareInterfaceDesignerReferenceFinding(findings, item, collection, fieldName, knownIds, index) {
    const value = String(item[fieldName] || "");
    const evidenceStatus = String(item.evidence_status || "");
    if (!value) {
      findings.push(hardwareInterfaceDesignerFinding(
        "broken_hardware_interface_reference",
        "error",
        `${collection}[${index}].${fieldName} is missing.`,
        `${collection}.${index}.${fieldName}`,
        "Fill the reference id or mark it as evidence_gap with evidence_status evidence_gap.",
      ));
      return;
    }
    if (value === "evidence_gap") {
      if (evidenceStatus !== "evidence_gap") {
        findings.push(hardwareInterfaceDesignerFinding(
          "broken_hardware_interface_reference",
          "error",
          `${collection}[${index}].${fieldName} is evidence_gap but evidence_status is ${evidenceStatus || "missing"}.`,
          `${collection}.${index}.${fieldName}`,
          "Set evidence_status to evidence_gap for unknown hardware references.",
        ));
      }
      return;
    }
    if (!knownIds.has(value)) {
      findings.push(hardwareInterfaceDesignerFinding(
        "broken_hardware_interface_reference",
        "error",
        `${collection}[${index}].${fieldName} references missing id ${value}.`,
        `${collection}.${index}.${fieldName}`,
        "Add the referenced sandbox record or mark the reference as evidence_gap.",
      ));
    }
  }

  function countHardwareInterfaceDesignerEvidenceGaps(payload) {
    let count = 0;
    for (const collection of ["lrus", "cables", "connectors", "ports", "pins", "bindings", "evidence_gaps"]) {
      for (const item of payload[collection] || []) {
        for (const value of Object.values(item || {})) {
          if (value === "evidence_gap") count += 1;
        }
        if (item && item.evidence_status === "evidence_gap") count += 1;
      }
    }
    return count;
  }

  function buildHardwareInterfaceDesignerValidationReport(payload) {
    const normalized = normalizeHardwareInterfaceDesignerPayload(payload);
    const findings = [];
    const truthChecks = [
      ["$schema", hardwareInterfaceDesignerSchemaId],
      ["kind", hardwareInterfaceDesignerKind],
      ["version", hardwareInterfaceDesignerVersion],
      ["candidate_state", "sandbox_candidate"],
      ["truth_level_impact", "none"],
      ["dal_pssa_impact", "none"],
      ["controller_truth_modified", false],
      ["runtime_truth_effect", "none"],
    ];
    for (const [fieldName, expected] of truthChecks) {
      if (normalized[fieldName] !== expected) {
        findings.push(hardwareInterfaceDesignerFinding(
          "hardware_interface_truth_boundary_violation",
          "error",
          `hardware_interface_designer ${fieldName} must be ${expected}.`,
          fieldName,
          "Restore sandbox-only hardware/interface design constants.",
        ));
      }
    }
    if (normalized.boundaries.runtime_scope !== "sandbox_only") {
      findings.push(hardwareInterfaceDesignerFinding(
        "hardware_interface_truth_boundary_violation",
        "error",
        "hardware_interface_designer boundaries.runtime_scope must be sandbox_only.",
        "boundaries.runtime_scope",
        "Keep hardware/interface design in sandbox scope only.",
      ));
    }
    if (normalized.boundaries.hardware_truth_effect !== "none") {
      findings.push(hardwareInterfaceDesignerFinding(
        "hardware_interface_truth_boundary_violation",
        "error",
        "hardware_interface_designer boundaries.hardware_truth_effect must be none.",
        "boundaries.hardware_truth_effect",
        "Hardware/interface fields are review evidence only.",
      ));
    }
    if (normalized.boundaries.certified_truth_modified !== false) {
      findings.push(hardwareInterfaceDesignerFinding(
        "hardware_interface_truth_boundary_violation",
        "error",
        "hardware_interface_designer boundaries.certified_truth_modified must be false.",
        "boundaries.certified_truth_modified",
        "Do not mark sandbox design as certified truth.",
      ));
    }
    if (normalized.boundaries.dal_pssa_impact !== "none") {
      findings.push(hardwareInterfaceDesignerFinding(
        "hardware_interface_truth_boundary_violation",
        "error",
        "hardware_interface_designer boundaries.dal_pssa_impact must be none.",
        "boundaries.dal_pssa_impact",
        "DAL/PSSA-impacting changes must leave this sandbox lane.",
      ));
    }

    addHardwareInterfaceDesignerDuplicateFindings(normalized, findings);
    const ids = hardwareInterfaceDesignerCollectionIds(normalized);
    for (const [index, cable] of normalized.cables.entries()) {
      addHardwareInterfaceDesignerReferenceFinding(findings, cable, "cables", "source_lru_id", ids.lrus, index);
      addHardwareInterfaceDesignerReferenceFinding(findings, cable, "cables", "target_lru_id", ids.lrus, index);
    }
    for (const [index, connector] of normalized.connectors.entries()) {
      addHardwareInterfaceDesignerReferenceFinding(findings, connector, "connectors", "lru_id", ids.lrus, index);
    }
    for (const [index, port] of normalized.ports.entries()) {
      addHardwareInterfaceDesignerReferenceFinding(findings, port, "ports", "connector_id", ids.connectors, index);
    }
    const portConnectorById = new Map(normalized.ports.map((port) => [String(port.id || ""), String(port.connector_id || "")]));
    for (const [index, pin] of normalized.pins.entries()) {
      addHardwareInterfaceDesignerReferenceFinding(findings, pin, "pins", "connector_id", ids.connectors, index);
      addHardwareInterfaceDesignerReferenceFinding(findings, pin, "pins", "port_id", ids.ports, index);
      const portConnector = portConnectorById.get(String(pin.port_id || ""));
      if (
        pin.port_id !== "evidence_gap"
        && pin.connector_id !== "evidence_gap"
        && portConnector
        && portConnector !== String(pin.connector_id || "")
      ) {
        findings.push(hardwareInterfaceDesignerFinding(
          "broken_hardware_interface_reference",
          "error",
          `pins[${index}].connector_id must match its port connector_id.`,
          `pins.${index}.connector_id`,
          "Align pin connector_id with the referenced port connector_id.",
        ));
      }
    }
    for (const [index, binding] of normalized.bindings.entries()) {
      if (binding.truth_effect !== "none") {
        findings.push(hardwareInterfaceDesignerFinding(
          "hardware_interface_truth_boundary_violation",
          "error",
          `bindings[${index}].truth_effect must be none.`,
          `bindings.${index}.truth_effect`,
          "Signal bindings are sandbox review evidence only.",
        ));
      }
      addHardwareInterfaceDesignerReferenceFinding(findings, binding, "bindings", "source_port_id", ids.ports, index);
      addHardwareInterfaceDesignerReferenceFinding(findings, binding, "bindings", "target_port_id", ids.ports, index);
      addHardwareInterfaceDesignerReferenceFinding(findings, binding, "bindings", "cable_id", ids.cables, index);
    }
    const evidenceGapCount = countHardwareInterfaceDesignerEvidenceGaps(normalized);
    if (evidenceGapCount > 0) {
      findings.push(hardwareInterfaceDesignerFinding(
        "hardware_interface_evidence_gap",
        "warning",
        `${evidenceGapCount} hardware/interface evidence gap marker(s) remain.`,
        "evidence_gaps",
        "Keep unknowns explicit as evidence_gap until source evidence is available.",
      ));
    }
    const hasError = findings.some((finding) => finding.severity === "error");
    const hasWarning = findings.some((finding) => finding.severity === "warning");
    return {
      kind: hardwareInterfaceDesignerValidationKind,
      version: hardwareInterfaceDesignerValidationVersion,
      design_id: String(normalized.design_id || "ui_draft_hardware_interface_design_v1"),
      system_id: String(normalized.system_id || "thrust-reverser"),
      status: hasError ? "fail" : (hasWarning ? "warn" : "pass"),
      finding_count: findings.length,
      error_count: findings.filter((finding) => finding.severity === "error").length,
      warning_count: findings.filter((finding) => finding.severity === "warning").length,
      evidence_gap_count: evidenceGapCount,
      counts: {
        lrus: normalized.lrus.length,
        cables: normalized.cables.length,
        connectors: normalized.connectors.length,
        ports: normalized.ports.length,
        pins: normalized.pins.length,
        bindings: normalized.bindings.length,
        evidence_gaps: normalized.evidence_gaps.length,
      },
      findings,
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_effect: "none",
    };
  }

  function validateHardwareInterfaceDesignerPayload(payload) {
    const normalized = normalizeHardwareInterfaceDesignerPayload(payload);
    const report = buildHardwareInterfaceDesignerValidationReport(normalized);
    if (report.status === "fail") {
      const firstFinding = report.findings[0] || {};
      throw new Error(firstFinding.message || "hardware interface designer validation failed");
    }
    return normalized;
  }

  function renderHardwareInterfaceDesignerValidationReport(report) {
    const normalizedReport = report || buildHardwareInterfaceDesignerValidationReport(
      currentHardwareInterfaceDesignerPayload("validation"),
    );
    lastHardwareInterfaceDesignerValidationReport = normalizedReport;
    if (hardwareInterfaceDesignValidationOutput) {
      hardwareInterfaceDesignValidationOutput.value = JSON.stringify(normalizedReport, null, 2);
    }
    if (hardwareInterfaceDesignStatus) {
      hardwareInterfaceDesignStatus.textContent =
        `Hardware/interface design ${normalizedReport.status}: ${normalizedReport.finding_count || 0} finding(s). Truth effect: none.`;
    }
    return normalizedReport;
  }

  function normalizeImportedHardwareInterfaceDesignerPayload(payload) {
    if (!payload || typeof payload !== "object" || Array.isArray(payload)) return null;
    return normalizeHardwareInterfaceDesignerPayload(payload);
  }

  function normalizeImportedHardwareInterfaceDesignerValidation(report) {
    if (!report || typeof report !== "object" || Array.isArray(report)) return null;
    return {
      ...report,
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_effect: "none",
    };
  }

  function parseHardwareInterfaceDesignerEditorPayload() {
    if (!hardwareInterfaceDesignOutput) return null;
    const raw = String(hardwareInterfaceDesignOutput.value || "").trim();
    if (!raw) return null;
    return JSON.parse(raw);
  }

  function currentHardwareInterfaceDesignerPayload(_state) {
    if (lastHardwareInterfaceDesignerPayload) {
      return normalizeHardwareInterfaceDesignerPayload(lastHardwareInterfaceDesignerPayload);
    }
    try {
      const editorPayload = parseHardwareInterfaceDesignerEditorPayload();
      if (editorPayload) return normalizeHardwareInterfaceDesignerPayload(editorPayload);
    } catch (_err) {
      return emptyHardwareInterfaceDesignerPayload();
    }
    return emptyHardwareInterfaceDesignerPayload();
  }

  function currentHardwareInterfaceDesignerValidationReport(state) {
    const payload = currentHardwareInterfaceDesignerPayload(state || "current");
    return buildHardwareInterfaceDesignerValidationReport(payload);
  }

  function exportHardwareInterfaceDesigner() {
    const payload = currentHardwareInterfaceDesignerPayload("export");
    const report = buildHardwareInterfaceDesignerValidationReport(payload);
    lastHardwareInterfaceDesignerPayload = payload;
    lastHardwareInterfaceDesignerValidationReport = report;
    if (hardwareInterfaceDesignOutput) {
      hardwareInterfaceDesignOutput.value = JSON.stringify(payload, null, 2);
    }
    renderHardwareInterfaceDesignerValidationReport(report);
    return payload;
  }

  function validateHardwareInterfaceDesignerFromEditor() {
    try {
      const payload = normalizeHardwareInterfaceDesignerPayload(
        parseHardwareInterfaceDesignerEditorPayload() || emptyHardwareInterfaceDesignerPayload(),
      );
      const report = buildHardwareInterfaceDesignerValidationReport(payload);
      lastHardwareInterfaceDesignerValidationReport = report;
      if (hardwareInterfaceDesignValidationOutput) {
        hardwareInterfaceDesignValidationOutput.value = JSON.stringify(report, null, 2);
      }
      if (hardwareInterfaceDesignStatus) {
        hardwareInterfaceDesignStatus.textContent =
          `Hardware/interface design ${report.status}: ${report.finding_count || 0} finding(s). Truth effect: none.`;
      }
      return report;
    } catch (err) {
      const report = {
        kind: hardwareInterfaceDesignerValidationKind,
        version: hardwareInterfaceDesignerValidationVersion,
        design_id: "parse_error",
        system_id: "thrust-reverser",
        status: "fail",
        finding_count: 1,
        error_count: 1,
        warning_count: 0,
        evidence_gap_count: 0,
        counts: {},
        findings: [hardwareInterfaceDesignerFinding(
          "hardware_interface_parse_error",
          "error",
          err && err.message ? err.message : "hardware interface design JSON parse failed",
          "hardware_interface_designer",
          "Fix JSON syntax before validating.",
        )],
        candidate_state: "sandbox_candidate",
        certification_claim: "none",
        truth_effect: "none",
      };
      renderHardwareInterfaceDesignerValidationReport(report);
      return report;
    }
  }

  function applyHardwareInterfaceDesignerFromEditor() {
    try {
      const payload = normalizeHardwareInterfaceDesignerPayload(
        parseHardwareInterfaceDesignerEditorPayload() || emptyHardwareInterfaceDesignerPayload(),
      );
      const report = buildHardwareInterfaceDesignerValidationReport(payload);
      renderHardwareInterfaceDesignerValidationReport(report);
      if (report.status === "fail") return null;
      lastHardwareInterfaceDesignerPayload = validateHardwareInterfaceDesignerPayload(payload);
      lastHardwareInterfaceDesignerValidationReport = report;
      if (hardwareInterfaceDesignOutput) {
        hardwareInterfaceDesignOutput.value = JSON.stringify(lastHardwareInterfaceDesignerPayload, null, 2);
      }
      recordEditableHistory("hardware_interface_designer_apply");
      recordWorkspaceAction("hardware_interface_designer_apply");
      recordCanvasInteractionAction("hardware_interface_designer_apply");
      shell.setAttribute("data-draft-state", "derived");
      if (draftLabel) draftLabel.textContent = "sandbox_candidate hardware/interface design applied";
      if (hardwareInterfaceDesignStatus) {
        hardwareInterfaceDesignStatus.textContent =
          `Applied hardware/interface design with ${report.counts.bindings || 0} binding(s). Truth effect: none.`;
      }
      renderWorkspaceDocumentStatus();
      persistDraft();
      return lastHardwareInterfaceDesignerPayload;
    } catch (err) {
      if (hardwareInterfaceDesignStatus) {
        hardwareInterfaceDesignStatus.textContent =
          err && err.message ? err.message : "hardware interface design apply failed";
      }
      return null;
    }
  }

  function hardwareBindingOwnerKey(binding) {
    if (!binding || typeof binding !== "object") return "unknown:unknown";
    return `${binding.owner_kind || "unknown"}:${binding.owner_id || "unknown"}`;
  }

  function hardwareBindingEvidenceGapFields(binding) {
    const source = binding && typeof binding === "object" ? binding : {};
    const fields = interfaceBindingRequiredFields
      .filter((fieldName) => isInterfaceEvidenceGap(source[fieldName]));
    if (source.evidence_status !== "ui_draft") {
      fields.push("evidence_status");
    }
    return fields;
  }

  function hardwareBindingInterfaceKey(binding) {
    if (!binding || typeof binding !== "object") return "";
    const hardwareId = normalizedInterfaceField(binding.hardware_id);
    const connector = normalizedInterfaceField(binding.connector);
    const portLocal = normalizedInterfaceField(binding.port_local);
    const portPeer = normalizedInterfaceField(binding.port_peer);
    if (
      isInterfaceEvidenceGap(hardwareId)
      || isInterfaceEvidenceGap(connector)
      || isInterfaceEvidenceGap(portLocal)
      || isInterfaceEvidenceGap(portPeer)
    ) {
      return "";
    }
    return [hardwareId, connector, portLocal, portPeer].join("|");
  }

  function normalizeDiagnosticEdgeIndex(value) {
    const numeric = Number.parseInt(String(value === null || value === undefined ? "" : value), 10);
    return Number.isInteger(numeric) && numeric >= 0 ? numeric : null;
  }

  function normalizeHardwareBindingFocusTarget(target, issue) {
    const source = target && typeof target === "object" ? target : {};
    const ownerKey = normalizedInterfaceField(source.owner_key || (issue && issue.target) || "unknown:unknown");
    const rawKind = normalizedInterfaceField(source.target_kind || source.kind || ownerKey.split(":")[0]);
    const targetKind = rawKind === "edge" || rawKind === "node" ? rawKind : "unknown";
    const edgeIndex = normalizeDiagnosticEdgeIndex(source.edge_index);
    const targetId = normalizedInterfaceField(
      source.target_id
        || source.node_id
        || source.edge_id
        || ownerKey.split(":").slice(1).join(":")
        || "unknown",
    );
    const focus = {
      kind: targetKind,
      target_kind: targetKind,
      target_id: targetId,
      owner_key: ownerKey,
      rule_id: normalizedInterfaceField(source.rule_id || (issue && issue.rule_id) || "hardware_binding_diagnostic"),
      issue_target: normalizedInterfaceField(source.issue_target || (issue && issue.target) || ownerKey),
      focus_effect: "selection_only",
      truth_effect: "none",
    };
    if (targetKind === "node") {
      focus.node_id = normalizedInterfaceField(source.node_id || targetId);
      if (source.node_index !== undefined) {
        const nodeIndex = normalizeDiagnosticEdgeIndex(source.node_index);
        if (nodeIndex !== null) focus.node_index = nodeIndex;
      }
    }
    if (targetKind === "edge") {
      focus.edge_id = normalizedInterfaceField(source.edge_id || targetId);
      if (edgeIndex !== null) focus.edge_index = edgeIndex;
      focus.source_node_id = normalizedInterfaceField(source.source_node_id || source.sourceNodeId || "unknown");
      focus.target_node_id = normalizedInterfaceField(source.target_node_id || source.targetNodeId || "unknown");
      focus.signal_id = normalizedInterfaceField(source.signal_id || source.signalId || "evidence_gap");
    }
    return focus;
  }

  function hardwareBindingFocusTarget(binding, issue) {
    if (!binding || typeof binding !== "object") {
      return normalizeHardwareBindingFocusTarget({}, issue);
    }
    if (binding.focus_target && typeof binding.focus_target === "object") {
      return normalizeHardwareBindingFocusTarget(binding.focus_target, issue);
    }
    return normalizeHardwareBindingFocusTarget({
      kind: binding.owner_kind,
      target_kind: binding.owner_kind,
      target_id: binding.owner_id,
      owner_key: hardwareBindingOwnerKey(binding),
    }, issue);
  }

  function uniqueHardwareBindingFocusTargets(bindings, issue) {
    const targets = [];
    const seen = new Set();
    for (const binding of Array.isArray(bindings) ? bindings : []) {
      const target = hardwareBindingFocusTarget(binding, issue);
      const key = [
        target.target_kind,
        target.target_id,
        target.edge_index !== undefined ? target.edge_index : "",
        target.node_index !== undefined ? target.node_index : "",
      ].join("|");
      if (target.target_kind === "unknown" || seen.has(key)) continue;
      seen.add(key);
      targets.push(target);
    }
    return targets;
  }

  function pushHardwareBindingDiagnosticIssue(issues, issue) {
    const focusTargets = Array.isArray(issue.focus_targets)
      ? issue.focus_targets.map((target) => normalizeHardwareBindingFocusTarget(target, issue))
      : [];
    const primaryFocus = issue.focus_target
      ? normalizeHardwareBindingFocusTarget(issue.focus_target, issue)
      : (focusTargets[0] || null);
    issues.push({
      severity: "warning",
      evidence_refs: [],
      truth_effect: "none",
      ...issue,
      focus_target: primaryFocus,
      focus_targets: focusTargets,
      focus_state: primaryFocus ? "focusable" : "unfocusable",
    });
  }

  function buildHardwareBindingDiagnosticsReport(bindings) {
    const rows = Array.isArray(bindings) ? bindings : [];
    const coverage = buildInterfaceBindingCoverageSummary(rows);
    const issues = [];
    const duplicateOwnerBindings = [];
    const reusedInterfaceKeys = [];
    const ownerGroups = new Map();
    const interfaceKeyGroups = new Map();
    let evidenceGapFieldCount = 0;

    for (const binding of rows) {
      const ownerKey = hardwareBindingOwnerKey(binding);
      if (!ownerGroups.has(ownerKey)) ownerGroups.set(ownerKey, []);
      ownerGroups.get(ownerKey).push(binding);

      const interfaceKey = hardwareBindingInterfaceKey(binding);
      if (interfaceKey) {
        if (!interfaceKeyGroups.has(interfaceKey)) interfaceKeyGroups.set(interfaceKey, []);
        interfaceKeyGroups.get(interfaceKey).push(binding);
      }

      const gapFields = hardwareBindingEvidenceGapFields(binding);
      evidenceGapFieldCount += gapFields.length;
      if (gapFields.length) {
        const focusTarget = hardwareBindingFocusTarget(binding, {
          rule_id: "evidence_gap_density",
          target: ownerKey,
        });
        pushHardwareBindingDiagnosticIssue(issues, {
          rule_id: "evidence_gap_density",
          target: ownerKey,
          target_kind: focusTarget.target_kind,
          target_id: focusTarget.target_id,
          message: `${ownerKey} has ${gapFields.length} evidence_gap field(s): ${gapFields.join(", ")}`,
          suggestion: "Record missing hardware/interface evidence before treating this candidate as review-ready.",
          evidence_refs: [binding.source_ref || "ui_draft.interface_binding"],
          focus_target: focusTarget,
          focus_targets: [focusTarget],
        });
      }
    }

    for (const [ownerKey, grouped] of ownerGroups.entries()) {
      if (grouped.length <= 1) continue;
      const entry = {
        owner_key: ownerKey,
        binding_ids: grouped.map((binding) => binding.id || "unknown"),
        count: grouped.length,
        truth_effect: "none",
      };
      duplicateOwnerBindings.push(entry);
      const focusTargets = uniqueHardwareBindingFocusTargets(grouped, {
        rule_id: "duplicate_ownership",
        target: ownerKey,
      });
      pushHardwareBindingDiagnosticIssue(issues, {
        rule_id: "duplicate_ownership",
        severity: "error",
        target: ownerKey,
        target_kind: focusTargets[0] ? focusTargets[0].target_kind : "unknown",
        target_id: focusTargets[0] ? focusTargets[0].target_id : ownerKey,
        message: `Duplicate owner binding detected for ${ownerKey}.`,
        suggestion: "Keep one sandbox binding per node/edge owner or split the owner into separate interface objects.",
        evidence_refs: grouped.map((binding) => binding.source_ref || binding.id || ownerKey),
        focus_target: focusTargets[0] || null,
        focus_targets: focusTargets,
      });
    }

    for (const [interfaceKey, grouped] of interfaceKeyGroups.entries()) {
      const ownerKeys = grouped.map((binding) => hardwareBindingOwnerKey(binding));
      const uniqueOwners = Array.from(new Set(ownerKeys));
      if (uniqueOwners.length <= 1) continue;
      const [hardwareId, connector, portLocal, portPeer] = interfaceKey.split("|");
      const entry = {
        interface_key: interfaceKey,
        hardware_id: hardwareId,
        connector,
        port_local: portLocal,
        port_peer: portPeer,
        owners: uniqueOwners,
        count: grouped.length,
        truth_effect: "none",
      };
      reusedInterfaceKeys.push(entry);
      const focusTargets = uniqueHardwareBindingFocusTargets(grouped, {
        rule_id: "connector_port_reuse",
        target: interfaceKey,
      });
      pushHardwareBindingDiagnosticIssue(issues, {
        rule_id: "connector_port_reuse",
        severity: "warning",
        target: interfaceKey,
        target_kind: focusTargets[0] ? focusTargets[0].target_kind : "unknown",
        target_id: focusTargets[0] ? focusTargets[0].target_id : interfaceKey,
        message: `Connector/port reuse detected on ${hardwareId} ${connector} ${portLocal}->${portPeer}.`,
        suggestion: "Verify whether the shared connector/port is intentional or assign a distinct interface key.",
        evidence_refs: grouped.map((binding) => binding.source_ref || hardwareBindingOwnerKey(binding)),
        focus_target: focusTargets[0] || null,
        focus_targets: focusTargets,
      });
    }

    const totalEvidenceFields = rows.length * (interfaceBindingRequiredFields.length + 1);
    const evidenceGapDensity = totalEvidenceFields
      ? Number((evidenceGapFieldCount / totalEvidenceFields).toFixed(4))
      : 0;
    return {
      kind: "well-harness-workbench-hardware-binding-diagnostics",
      version: 1,
      status: issues.some((issue) => issue.severity === "error")
        ? "fail"
        : (issues.length ? "warn" : "pass"),
      binding_count: rows.length,
      complete_count: coverage.complete,
      partial_count: coverage.partial,
      missing_count: coverage.missing,
      evidence_gap_field_count: evidenceGapFieldCount,
      evidence_gap_density: evidenceGapDensity,
      duplicate_owner_bindings: duplicateOwnerBindings,
      reused_interface_keys: reusedInterfaceKeys,
      issue_count: issues.length,
      issues,
      truth_effect: "none",
    };
  }

  function hardwareDiagnosticFocusKey(focus) {
    if (!focus || typeof focus !== "object") return "";
    return [
      focus.target_kind || focus.kind || "unknown",
      focus.target_id || focus.node_id || focus.edge_id || "unknown",
      focus.edge_index !== undefined && focus.edge_index !== null ? focus.edge_index : "",
      focus.node_index !== undefined && focus.node_index !== null ? focus.node_index : "",
    ].join("|");
  }

  function hardwareDiagnosticFocusMatchesSelected(focus) {
    return Boolean(
      selectedDiagnosticFocus
        && hardwareDiagnosticFocusKey(selectedDiagnosticFocus) === hardwareDiagnosticFocusKey(focus),
    );
  }

  function hardwareDiagnosticFocusAttributes(focus, issueIndex, targetIndex) {
    const target = normalizeHardwareBindingFocusTarget(focus || {}, {
      rule_id: focus && focus.rule_id,
      target: focus && focus.issue_target,
    });
    const attrs = [
      'data-diagnostics-focus="true"',
      `data-diagnostics-issue-index="${issueIndex}"`,
      `data-diagnostics-target-index="${targetIndex}"`,
      `data-diagnostics-target-kind="${inspectorText(target.target_kind)}"`,
      `data-diagnostics-target-id="${inspectorText(target.target_id)}"`,
      `data-diagnostics-owner-key="${inspectorText(target.owner_key)}"`,
      `data-diagnostics-rule-id="${inspectorText(target.rule_id)}"`,
      `data-diagnostics-issue-target="${inspectorText(target.issue_target)}"`,
    ];
    if (target.node_id) attrs.push(`data-diagnostics-node-id="${inspectorText(target.node_id)}"`);
    if (target.node_index !== undefined) attrs.push(`data-diagnostics-node-index="${target.node_index}"`);
    if (target.edge_id) attrs.push(`data-diagnostics-edge-id="${inspectorText(target.edge_id)}"`);
    if (target.edge_index !== undefined) attrs.push(`data-diagnostics-edge-index="${target.edge_index}"`);
    if (target.signal_id) attrs.push(`data-diagnostics-signal-id="${inspectorText(target.signal_id)}"`);
    if (target.source_node_id) attrs.push(`data-diagnostics-source-node-id="${inspectorText(target.source_node_id)}"`);
    if (target.target_node_id) attrs.push(`data-diagnostics-target-node-id="${inspectorText(target.target_node_id)}"`);
    return attrs.join(" ");
  }

  function renderHardwareDiagnosticFocusTarget(focus, issueIndex, targetIndex) {
    const target = normalizeHardwareBindingFocusTarget(focus || {}, {
      rule_id: focus && focus.rule_id,
      target: focus && focus.issue_target,
    });
    if (target.target_kind === "unknown") return "";
    const label = target.target_kind === "edge"
      ? `Focus edge ${target.edge_id || target.target_id}#${target.edge_index !== undefined ? target.edge_index : "?"}`
      : `Focus node ${target.node_id || target.target_id}`;
    const active = hardwareDiagnosticFocusMatchesSelected(target);
    return [
      '<button',
      'type="button"',
      'class="workbench-binding-diagnostics-target"',
      hardwareDiagnosticFocusAttributes(target, issueIndex, targetIndex),
      `aria-pressed="${active ? "true" : "false"}"`,
      '>',
      inspectorText(label),
      '</button>',
    ].join(" ");
  }

  function renderHardwareDiagnosticFocusTargets(issue, issueIndex) {
    const targets = Array.isArray(issue.focus_targets)
      ? issue.focus_targets
      : (issue.focus_target ? [issue.focus_target] : []);
    const buttons = targets
      .map((target, index) => renderHardwareDiagnosticFocusTarget(target, issueIndex, index))
      .filter(Boolean);
    if (!buttons.length) {
      return '<small class="workbench-binding-diagnostics-focus-empty">No selectable sandbox target.</small>';
    }
    return [
      '<div class="workbench-binding-diagnostics-targets">',
      buttons.join(""),
      '</div>',
    ].join("");
  }

  function normalizeRepairActionId(actionId) {
    const text = normalizedInterfaceField(actionId);
    return [
      "clear_binding",
      "mark_evidence_gap",
      "copy_explicit_fingerprint",
    ].includes(text) ? text : "unknown_repair_action";
  }

  function repairActionTargetMetadata(target) {
    const source = target && typeof target === "object" ? target : {};
    const sourceKind = source.kind || source.target_kind;
    const activeTarget = sourceKind
      ? {
          kind: sourceKind,
          id: source.id || source.target_id || source.targetId,
        }
      : activeInterfaceBindingTarget();
    const focus = (
      source.diagnostic_focus
      && typeof source.diagnostic_focus === "object"
      && !Array.isArray(source.diagnostic_focus)
    )
      ? source.diagnostic_focus
      : (selectedDiagnosticFocus || currentDiagnosticFocusSummary());
    return {
      target_kind: activeTarget.kind || focus.target_kind || "unknown",
      target_id: activeTarget.id || focus.target_id || "unknown",
      diagnostic_focus: focus && focus.state !== "none"
        ? normalizeHardwareBindingFocusTarget(focus)
        : currentDiagnosticFocusSummary(),
      truth_effect: "none",
    };
  }

  function normalizeRepairChangedFields(fields) {
    return (Array.isArray(fields) ? fields : [])
      .filter((field) => field && typeof field === "object")
      .map((field) => ({
        field: normalizedInterfaceField(field.field || "unknown"),
        before: normalizedInterfaceField(field.before),
        after: normalizedInterfaceField(field.after),
      }));
  }

  function normalizeRepairActionLogEntry(entry, fallbackIndex) {
    const source = entry && typeof entry === "object" ? entry : {};
    const actionId = normalizeRepairActionId(source.action_id || source.actionId);
    const target = repairActionTargetMetadata(source.target || source.focus_target || {});
    return {
      kind: "well-harness-workbench-diagnostic-repair-action",
      version: 1,
      id: normalizedInterfaceField(source.id || `${actionId}_${fallbackIndex || 1}`),
      action_id: actionId,
      recorded_at: normalizedInterfaceField(source.recorded_at || source.timestamp || "browser_local_draft"),
      target,
      diagnostic_source: {
        rule_id: normalizedInterfaceField(
          (source.diagnostic_source && source.diagnostic_source.rule_id)
            || (target.diagnostic_focus && target.diagnostic_focus.rule_id)
            || "hardware_binding_diagnostic",
        ),
        issue_target: normalizedInterfaceField(
          (source.diagnostic_source && source.diagnostic_source.issue_target)
            || (target.diagnostic_focus && target.diagnostic_focus.issue_target)
            || "unknown",
        ),
        truth_effect: "none",
      },
      changed_fields: normalizeRepairChangedFields(source.changed_fields || source.changedFields),
      before_checksum: normalizedInterfaceField(source.before_checksum || source.beforeChecksum),
      after_checksum: normalizedInterfaceField(source.after_checksum || source.afterChecksum),
      source_binding: source.source_binding && typeof source.source_binding === "object"
        ? {
            owner_kind: normalizedInterfaceField(source.source_binding.owner_kind),
            owner_id: normalizedInterfaceField(source.source_binding.owner_id),
            source_ref: normalizedInterfaceField(source.source_binding.source_ref),
            truth_effect: "none",
          }
        : null,
      truth_effect: "none",
    };
  }

  function normalizeRepairActionLog(entries) {
    return (Array.isArray(entries) ? entries : [])
      .map((entry, index) => normalizeRepairActionLogEntry(entry, index + 1));
  }

  function repairActionLogSnapshot() {
    return normalizeRepairActionLog(repairActionLog);
  }

  function explicitRepairCopySourceForFocus() {
    if (!selectedDiagnosticFocus) return null;
    const target = activeInterfaceBindingTarget();
    const focus = normalizeHardwareBindingFocusTarget(selectedDiagnosticFocus);
    const rows = collectWorkbenchHardwareBindings();
    const eligibleRows = rows.filter((binding) => (
      binding
      && binding.evidence_status === "ui_draft"
      && interfaceBindingRequiredFields.every((fieldName) => !isInterfaceEvidenceGap(binding[fieldName]))
      && !(
        binding.owner_kind === target.kind
        && binding.owner_id === target.id
        && (
          focus.edge_index === undefined
          || !binding.focus_target
          || binding.focus_target.edge_index === focus.edge_index
        )
      )
    ));
    if (!eligibleRows.length) return null;
    const scoped = eligibleRows.filter((binding) => (
      hardwareBindingOwnerKey(binding) === focus.issue_target
      || hardwareBindingInterfaceKey(binding) === focus.issue_target
    ));
    return scoped[0] || null;
  }

  function renderHardwareDiagnosticRepairPanel() {
    if (!selectedDiagnosticFocus) return "";
    const target = activeInterfaceBindingTarget();
    if (target.kind === "none") return "";
    const focus = normalizeHardwareBindingFocusTarget(selectedDiagnosticFocus);
    const copySource = explicitRepairCopySourceForFocus();
    const copyLabel = copySource
      ? `Copy ${copySource.owner_kind}:${copySource.owner_id}`
      : "Copy explicit fingerprint";
    return [
      '<div class="workbench-binding-diagnostics-repair-panel" data-repair-state="ready">',
      '<strong>Repair selected binding</strong>',
      `<span>${inspectorText(target.kind)}:${inspectorText(target.id)} · ${inspectorText(focus.rule_id)}</span>`,
      '<div class="workbench-binding-diagnostics-repair-actions">',
      '<button type="button" class="workbench-binding-diagnostics-repair-action" data-diagnostics-repair-action="clear_binding">Clear binding</button>',
      '<button type="button" class="workbench-binding-diagnostics-repair-action" data-diagnostics-repair-action="mark_evidence_gap">Mark gaps</button>',
      '<button type="button" class="workbench-binding-diagnostics-repair-action" data-diagnostics-repair-action="copy_explicit_fingerprint"',
      copySource ? "" : ' disabled="disabled"',
      '>',
      inspectorText(copyLabel),
      '</button>',
      '</div>',
      '<small>Sandbox draft repair only · truth_effect: none</small>',
      '</div>',
    ].join(" ");
  }

  function renderHardwareBindingDiagnostics(report) {
    const diagnostics = report || buildHardwareBindingDiagnosticsReport(collectWorkbenchHardwareBindings());
    if (hardwareBindingDiagnosticsStatus) {
      hardwareBindingDiagnosticsStatus.textContent = diagnostics.status;
    }
    if (hardwareBindingDiagnosticsCount) {
      hardwareBindingDiagnosticsCount.textContent = String(diagnostics.binding_count || 0);
    }
    if (hardwareBindingDiagnosticsGapCount) {
      hardwareBindingDiagnosticsGapCount.textContent = String(diagnostics.evidence_gap_field_count || 0);
    }
    if (!hardwareBindingDiagnosticsList) return diagnostics;
    const issues = Array.isArray(diagnostics.issues) ? diagnostics.issues : [];
    if (!issues.length) {
      hardwareBindingDiagnosticsList.setAttribute("data-diagnostics-state", "empty");
      hardwareBindingDiagnosticsList.textContent =
        diagnostics.binding_count
          ? "No hardware binding conflicts detected. Truth effect: none."
          : "No sandbox hardware bindings to diagnose.";
      return diagnostics;
    }
    hardwareBindingDiagnosticsList.setAttribute("data-diagnostics-state", "ready");
    const repairPanel = renderHardwareDiagnosticRepairPanel();
    const issueHtml = issues.slice(0, 8).map((issue, issueIndex) => [
      '<article',
      'class="workbench-binding-diagnostics-item"',
      `data-severity="${inspectorText(issue.severity || "warning")}"`,
      `data-rule-id="${inspectorText(issue.rule_id || "hardware_binding_diagnostic")}"`,
      `data-target-kind="${inspectorText(issue.target_kind || (issue.focus_target && issue.focus_target.target_kind) || "unknown")}"`,
      `data-target-id="${inspectorText(issue.target_id || (issue.focus_target && issue.focus_target.target_id) || "workbench")}"`,
      '>',
      `<strong>${inspectorText(issue.rule_id || "hardware_binding_diagnostic")}</strong>`,
      `<span>${inspectorText(issue.message || "")}</span>`,
      `<small>${inspectorText(issue.target || "workbench")}</small>`,
      `<em>${inspectorText(issue.suggestion || "Review sandbox evidence before handoff.")}</em>`,
      renderHardwareDiagnosticFocusTargets(issue, issueIndex),
      '</article>',
    ].join(" ")).join("");
    hardwareBindingDiagnosticsList.innerHTML = [repairPanel, issueHtml].filter(Boolean).join("");
    return diagnostics;
  }

  function diagnosticFocusTargetFromElement(element) {
    if (!element) return null;
    return normalizeHardwareBindingFocusTarget({
      kind: element.getAttribute("data-diagnostics-target-kind"),
      target_kind: element.getAttribute("data-diagnostics-target-kind"),
      target_id: element.getAttribute("data-diagnostics-target-id"),
      owner_key: element.getAttribute("data-diagnostics-owner-key"),
      rule_id: element.getAttribute("data-diagnostics-rule-id"),
      issue_target: element.getAttribute("data-diagnostics-issue-target"),
      node_id: element.getAttribute("data-diagnostics-node-id"),
      node_index: element.getAttribute("data-diagnostics-node-index"),
      edge_id: element.getAttribute("data-diagnostics-edge-id"),
      edge_index: element.getAttribute("data-diagnostics-edge-index"),
      signal_id: element.getAttribute("data-diagnostics-signal-id"),
      source_node_id: element.getAttribute("data-diagnostics-source-node-id"),
      target_node_id: element.getAttribute("data-diagnostics-target-node-id"),
    });
  }

  function diagnosticFocusValueKnown(value) {
    return Boolean(value && value !== "evidence_gap" && value !== "unknown");
  }

  function edgeMatchesDiagnosticFocusIdentity(edge, target, options) {
    if (!edge || !target) return false;
    const allowIdOnly = Boolean(options && options.allowIdOnly);
    const signalKnown = diagnosticFocusValueKnown(target.signal_id);
    const routeKnown = (
      diagnosticFocusValueKnown(target.source_node_id)
      && diagnosticFocusValueKnown(target.target_node_id)
    );
    if (routeKnown && signalKnown) {
      return (
        edge.source === target.source_node_id
        && edge.target === target.target_node_id
        && edge.signal_id === target.signal_id
      );
    }
    if (
      routeKnown
      && !signalKnown
      && edge.source === target.source_node_id
      && edge.target === target.target_node_id
    ) return true;
    if (routeKnown) return false;
    if (signalKnown && edge.signal_id === target.signal_id) return true;
    if (!signalKnown && !routeKnown && allowIdOnly && diagnosticFocusValueKnown(target.edge_id)) {
      return edge.id === target.edge_id;
    }
    return false;
  }

  function findEdgeIndexForDiagnosticFocus(focus) {
    const target = normalizeHardwareBindingFocusTarget(focus || {});
    const indexed = normalizeDiagnosticEdgeIndex(target.edge_index);
    if (indexed !== null && draftEdges[indexed]) {
      const edge = draftEdges[indexed];
      if (edgeMatchesDiagnosticFocusIdentity(edge, target, { allowIdOnly: false })) {
        return indexed;
      }
    }
    if (target.edge_id && target.edge_id !== "evidence_gap") {
      const exactSignalIndex = draftEdges.findIndex((edge) => (
        edge.id === target.edge_id
        && edgeMatchesDiagnosticFocusIdentity(edge, target, { allowIdOnly: false })
      ));
      if (exactSignalIndex >= 0) return exactSignalIndex;
      return draftEdges.findIndex((edge) => (
        edge.id === target.edge_id
        && edgeMatchesDiagnosticFocusIdentity(edge, target, { allowIdOnly: true })
      ));
    }
    const exactSignalIndex = draftEdges.findIndex((edge) => (
      edgeMatchesDiagnosticFocusIdentity(edge, target, { allowIdOnly: false })
    ));
    if (exactSignalIndex >= 0) return exactSignalIndex;
    return -1;
  }

  function currentDiagnosticFocusSummary() {
    if (!selectedDiagnosticFocus) {
      return {
        state: "none",
        truth_effect: "none",
      };
    }
    return {
      ...selectedDiagnosticFocus,
      state: "selected",
      truth_effect: "none",
    };
  }

  function setSelectedDiagnosticFocus(focus) {
    selectedDiagnosticFocus = {
      ...normalizeHardwareBindingFocusTarget(focus || {}),
      selected_at: "browser_local_draft",
      truth_effect: "none",
    };
    return selectedDiagnosticFocus;
  }

  function focusHardwareBindingDiagnosticTarget(focus) {
    const target = normalizeHardwareBindingFocusTarget(focus || {});
    if (target.target_kind === "node") {
      refreshEditableNodes();
      const nodeId = target.node_id || target.target_id;
      const node = nodes.find((candidate) => editableNodeId(candidate) === nodeId);
      if (!node) {
        selectedDiagnosticFocus = null;
        if (graphValidationStatus) {
          graphValidationStatus.textContent =
            `Binding diagnostic target missing: node ${nodeId}. Truth effect: none.`;
        }
        renderHardwareBindingDiagnostics();
        return null;
      }
      const selectedFocus = setSelectedDiagnosticFocus(target);
      selectNode(node, { preserveDiagnosticFocus: true });
      if (graphValidationStatus) {
        graphValidationStatus.textContent =
          `Binding diagnostic focused node ${nodeId}. Repair binding in inspector. Truth effect: none.`;
      }
      return selectedFocus;
    }
    if (target.target_kind === "edge") {
      const edgeIndex = findEdgeIndexForDiagnosticFocus(target);
      if (edgeIndex < 0) {
        selectedDiagnosticFocus = null;
        if (graphValidationStatus) {
          graphValidationStatus.textContent =
            `Binding diagnostic target missing: edge ${target.edge_id || target.target_id}. Truth effect: none.`;
        }
        renderHardwareBindingDiagnostics();
        return null;
      }
      const edge = draftEdges[edgeIndex] || {};
      const selectedFocus = setSelectedDiagnosticFocus({
        ...target,
        target_id: edge.id || target.target_id,
        edge_id: edge.id || target.edge_id || target.target_id,
        edge_index: edgeIndex,
        source_node_id: edge.source || target.source_node_id,
        target_node_id: edge.target || target.target_node_id,
        signal_id: edge.signal_id || target.signal_id,
      });
      selectEditableEdgeByIndex(edgeIndex, { preserveDiagnosticFocus: true });
      if (graphValidationStatus) {
        graphValidationStatus.textContent =
          `Binding diagnostic focused edge ${edge.id || target.target_id}#${edgeIndex}. Repair binding in inspector. Truth effect: none.`;
      }
      return selectedFocus;
    }
    selectedDiagnosticFocus = null;
    if (graphValidationStatus) {
      graphValidationStatus.textContent = "Binding diagnostic has no selectable sandbox target. Truth effect: none.";
    }
    return null;
  }

  function handleHardwareBindingDiagnosticActivation(event) {
    const trigger = event && event.target instanceof Element
      ? event.target.closest("[data-diagnostics-focus='true']")
      : null;
    if (!trigger || !hardwareBindingDiagnosticsList || !hardwareBindingDiagnosticsList.contains(trigger)) return;
    if (event.type === "keydown" && event.key !== "Enter" && event.key !== " ") return;
    event.preventDefault();
    event.stopPropagation();
    const focus = diagnosticFocusTargetFromElement(trigger);
    focusHardwareBindingDiagnosticTarget(focus);
    renderHardwareBindingDiagnostics();
    updateEditableDraftHash();
    persistDraft();
  }

  function isRepairUnknownValue(value) {
    const text = String(value === null || value === undefined ? "" : value).trim().toLowerCase();
    return !text || ["evidence_gap", "unknown", "tbd", "not_recorded", "n/a", "na"].includes(text);
  }

  function repairBindingFields(binding) {
    const source = normalizeInterfaceBinding(binding || {}, "repair", "target");
    return {
      hardware_id: source.hardware_id,
      cable: source.cable,
      connector: source.connector,
      port_local: source.port_local,
      port_peer: source.port_peer,
      evidence_status: source.evidence_status,
      source_ref: source.source_ref,
    };
  }

  function changedRepairBindingFields(before, after) {
    const fields = [...interfaceBindingRequiredFields, "evidence_status", "source_ref"];
    return fields
      .filter((fieldName) => normalizedInterfaceField(before[fieldName]) !== normalizedInterfaceField(after[fieldName]))
      .map((fieldName) => ({
        field: fieldName,
        before: before[fieldName],
        after: after[fieldName],
      }));
  }

  function setActiveInterfaceBinding(target, binding) {
    if (!target || target.kind === "none") return null;
    if (target.kind === "edge") {
      return setEdgeInterfaceBinding(selectedEdge, binding);
    }
    if (target.kind === "node") {
      return setNodeInterfaceBinding(selectedNode, binding);
    }
    return null;
  }

  function buildDiagnosticRepairBinding(actionId, currentBinding, sourceBinding) {
    const source = currentBinding && typeof currentBinding === "object" ? currentBinding : {};
    if (actionId === "clear_binding") {
      return {
        hardware_id: "evidence_gap",
        cable: "evidence_gap",
        connector: "evidence_gap",
        port_local: "evidence_gap",
        port_peer: "evidence_gap",
        evidence_status: "evidence_gap",
        source_ref: "ui_draft.diagnostic_repair.clear_binding",
      };
    }
    if (actionId === "mark_evidence_gap") {
      const next = {
        hardware_id: isRepairUnknownValue(source.hardware_id) ? "evidence_gap" : source.hardware_id,
        cable: isRepairUnknownValue(source.cable) ? "evidence_gap" : source.cable,
        connector: isRepairUnknownValue(source.connector) ? "evidence_gap" : source.connector,
        port_local: isRepairUnknownValue(source.port_local) ? "evidence_gap" : source.port_local,
        port_peer: isRepairUnknownValue(source.port_peer) ? "evidence_gap" : source.port_peer,
        evidence_status: source.evidence_status === "ui_draft" ? "ui_draft" : "evidence_gap",
        source_ref: "ui_draft.diagnostic_repair.mark_evidence_gap",
      };
      return next;
    }
    if (actionId === "copy_explicit_fingerprint" && sourceBinding) {
      return {
        hardware_id: sourceBinding.hardware_id,
        cable: sourceBinding.cable,
        connector: sourceBinding.connector,
        port_local: sourceBinding.port_local,
        port_peer: sourceBinding.port_peer,
        evidence_status: sourceBinding.evidence_status,
        source_ref: `ui_draft.diagnostic_repair.copy_explicit.${sourceBinding.owner_kind}:${sourceBinding.owner_id}`,
      };
    }
    return null;
  }

  function appendDiagnosticRepairActionLog(actionId, target, before, after, changedFields, sourceBinding) {
    const focus = selectedDiagnosticFocus || currentDiagnosticFocusSummary();
    const rawEntry = {
      id: `repair_${repairActionLog.length + 1}_${actionId}`,
      action_id: actionId,
      recorded_at: "browser_local_draft",
      target: repairActionTargetMetadata(target),
      diagnostic_source: {
        rule_id: focus && focus.rule_id,
        issue_target: focus && focus.issue_target,
        truth_effect: "none",
      },
      changed_fields: changedFields,
      before_checksum: checksumEvidenceArchiveField(before),
      after_checksum: checksumEvidenceArchiveField(after),
      source_binding: sourceBinding ? {
        owner_kind: sourceBinding.owner_kind,
        owner_id: sourceBinding.owner_id,
        source_ref: sourceBinding.source_ref,
        truth_effect: "none",
      } : null,
      truth_effect: "none",
    };
    const entry = normalizeRepairActionLogEntry(rawEntry, repairActionLog.length + 1);
    repairActionLog = [...repairActionLog, entry].slice(-100);
    return entry;
  }

  function applyDiagnosticRepairAction(actionId) {
    const normalizedActionId = normalizeRepairActionId(actionId);
    if (!selectedDiagnosticFocus) {
      if (interfaceBindingStatus) {
        interfaceBindingStatus.textContent = "Focus a binding diagnostic before applying a repair action. Truth effect: none.";
      }
      return null;
    }
    const target = activeInterfaceBindingTarget();
    if (target.kind === "none") {
      if (interfaceBindingStatus) {
        interfaceBindingStatus.textContent = "Select a node or edge before applying a repair action. Truth effect: none.";
      }
      return null;
    }
    const sourceBinding = normalizedActionId === "copy_explicit_fingerprint"
      ? explicitRepairCopySourceForFocus()
      : null;
    const nextBinding = buildDiagnosticRepairBinding(normalizedActionId, target.binding, sourceBinding);
    if (!nextBinding) {
      if (interfaceBindingStatus) {
        interfaceBindingStatus.textContent =
          `Repair action ${normalizedActionId} has no explicit sandbox source. Truth effect: none.`;
      }
      return null;
    }
    recordEditableHistory(`diagnostic_repair_${normalizedActionId}`);
    shell.setAttribute("data-draft-state", "derived");
    const before = repairBindingFields(target.binding);
    const applied = setActiveInterfaceBinding(target, nextBinding);
    const after = repairBindingFields(applied || nextBinding);
    const changedFields = changedRepairBindingFields(before, after);
    const logEntry = appendDiagnosticRepairActionLog(
      normalizedActionId,
      target,
      before,
      after,
      changedFields,
      sourceBinding,
    );
    if (draftLabel) draftLabel.textContent = "sandbox_candidate diagnostic repair pending";
    renderInspector();
    renderEditableEdges();
    renderHardwareBindingDiagnostics();
    updateEditableDraftHash();
    persistDraft();
    if (interfaceBindingStatus) {
      interfaceBindingStatus.textContent =
        `Applied ${normalizedActionId} to ${target.kind}:${target.id}; changed ${changedFields.length} field(s). Truth effect: none.`;
    }
    return logEntry;
  }

  function handleHardwareBindingDiagnosticRepairActivation(event) {
    const trigger = event && event.target instanceof Element
      ? event.target.closest("[data-diagnostics-repair-action]")
      : null;
    if (!trigger || !hardwareBindingDiagnosticsList || !hardwareBindingDiagnosticsList.contains(trigger)) return;
    if (event.type === "keydown" && event.key !== "Enter" && event.key !== " ") return;
    event.preventDefault();
    event.stopPropagation();
    applyDiagnosticRepairAction(trigger.getAttribute("data-diagnostics-repair-action") || "");
  }

  function collectWorkbenchInterfacePorts() {
    return collectWorkbenchHardwareBindings().flatMap((binding) => [
      {
        id: `ui-port:${binding.owner_kind}:${binding.owner_id}:local`,
        owner_kind: binding.owner_kind,
        owner_id: binding.owner_id,
        port_id: binding.port_local,
        role: "local",
        evidence_status: binding.evidence_status,
        truth_effect: "none",
      },
      {
        id: `ui-port:${binding.owner_kind}:${binding.owner_id}:peer`,
        owner_kind: binding.owner_kind,
        owner_id: binding.owner_id,
        port_id: binding.port_peer,
        role: "peer",
        evidence_status: binding.evidence_status,
        truth_effect: "none",
      },
    ]).filter((port) => port.port_id && port.port_id !== "evidence_gap");
  }

  function buildInterfaceBindingCoverageSummary(bindings) {
    const counts = { missing: 0, partial: 0, complete: 0 };
    for (const binding of bindings || []) {
      const status = (binding && binding.binding_quality)
        || interfaceBindingQualityReport(binding).status;
      counts[status] = (counts[status] || 0) + 1;
    }
    return {
      total_bindings: (bindings || []).length,
      missing: counts.missing,
      partial: counts.partial,
      complete: counts.complete,
      required_fields: [...interfaceBindingRequiredFields, "evidence_status"],
      truth_effect: "none",
    };
  }

  function bindingCoverageText(summary) {
    return `Binding coverage: ${summary.complete} complete / ${summary.partial} partial / ${summary.missing} missing. Truth effect: none.`;
  }

  const portValueTypes = ["boolean", "number", "string", "state", "unknown"];

  function normalizePortValueType(value) {
    const text = normalizedInterfaceField(value);
    return portValueTypes.includes(text) ? text : "unknown";
  }

  function normalizePortRequired(value) {
    return value === true || value === "true" || value === "required";
  }

  function normalizePortField(value, defaultValue) {
    const text = String(value === null || value === undefined ? "" : value).trim();
    return text || defaultValue;
  }

  function normalizePortContract(contract, nodeId) {
    const source = contract && typeof contract === "object" ? contract : {};
    const normalizedNodeId = normalizePortField(nodeId || source.node_id || source.nodeId, "unknown");
    return {
      input_port_id: normalizePortField(
        source.input_port_id || source.inputPortId,
        `${normalizedNodeId}:in`,
      ),
      output_port_id: normalizePortField(
        source.output_port_id || source.outputPortId,
        `${normalizedNodeId}:out`,
      ),
      input_signal_id: normalizePortField(
        source.input_signal_id || source.inputSignalId,
        normalizedNodeId,
      ),
      output_signal_id: normalizePortField(
        source.output_signal_id || source.outputSignalId,
        normalizedNodeId,
      ),
      value_type: normalizePortValueType(source.value_type || source.valueType || "boolean"),
      unit: String(source.unit === null || source.unit === undefined ? "" : source.unit).trim(),
      required: normalizePortRequired(source.required),
      source_ref: normalizePortField(
        source.source_ref || source.sourceRef,
        "ui_draft.port_contract",
      ),
      truth_effect: "none",
    };
  }

  function portContractForCatalogNode(nodeId, entry) {
    const catalog = entry || operationCatalogEntry(selectedCatalogOp);
    return normalizePortContract({
      input_signal_id: `${nodeId}_${catalog.op}_input`,
      output_signal_id: `${nodeId}_${catalog.op}_output`,
      value_type: catalog.value_type,
      unit: "",
      required: catalog.op === "compare" || catalog.op === "between",
      source_ref: `ui_draft.op_catalog.${catalog.op}.port_contract`,
      truth_effect: "none",
    }, nodeId);
  }

  function normalizeRuleComparison(value) {
    const text = String(value === null || value === undefined ? "" : value).trim();
    return approvedRuleComparisons.includes(text) ? text : "==";
  }

  function parseRuleThresholdValue(rawValue) {
    const text = String(rawValue === null || rawValue === undefined ? "" : rawValue).trim();
    if (!text) return true;
    try {
      return JSON.parse(text);
    } catch (_err) {
      const numeric = Number(text);
      if (!Number.isNaN(numeric)) return numeric;
      return text;
    }
  }

  function ruleThresholdInputText(value) {
    if (value === null || value === undefined) return "";
    if (typeof value === "string") return value;
    return JSON.stringify(value);
  }

  function normalizeNodeDraftRule(rule, nodeId) {
    const source = rule && typeof rule === "object" ? rule : {};
    const normalizedNodeId = String(nodeId || "unknown").trim() || "unknown";
    return {
      name: normalizePortField(source.name, `${normalizedNodeId}_draft_rule`),
      source_signal_id: normalizePortField(
        source.source_signal_id || source.sourceSignalId,
        normalizedNodeId,
      ),
      comparison: normalizeRuleComparison(source.comparison),
      threshold_value: source.threshold_value !== undefined
        ? source.threshold_value
        : parseRuleThresholdValue(source.thresholdValue),
    };
  }

  function nodeDraftRulesTouched(node) {
    return node && node.getAttribute("data-rule-parameters-touched") === "true";
  }

  function setNodeDraftRules(node, rules) {
    if (!node) return [];
    const nodeId = node.getAttribute("data-editable-node-id") || "unknown";
    const normalizedRules = (Array.isArray(rules) ? rules : [])
      .map((rule) => normalizeNodeDraftRule(rule, nodeId));
    if (!normalizedRules.length) {
      node.removeAttribute("data-rule-name");
      node.removeAttribute("data-rule-source-signal");
      node.removeAttribute("data-rule-comparison");
      node.removeAttribute("data-rule-threshold-json");
      node.removeAttribute("data-rules-json");
      node.removeAttribute("data-rule-parameters-touched");
      return [];
    }
    const firstRule = normalizedRules[0];
    node.setAttribute("data-rule-name", firstRule.name);
    node.setAttribute("data-rule-source-signal", firstRule.source_signal_id);
    node.setAttribute("data-rule-comparison", firstRule.comparison);
    node.setAttribute("data-rule-threshold-json", JSON.stringify(firstRule.threshold_value));
    node.setAttribute("data-rules-json", JSON.stringify(normalizedRules));
    node.setAttribute("data-rule-parameters-touched", "true");
    node.setAttribute("data-rule-count", String(normalizedRules.length));
    updateNodeDisplay(node);
    return normalizedRules;
  }

  function nodeDraftRules(node) {
    if (!node || !nodeDraftRulesTouched(node)) return [];
    const nodeId = node.getAttribute("data-editable-node-id") || "unknown";
    const rulesJson = node.getAttribute("data-rules-json");
    if (rulesJson) {
      try {
        const parsed = JSON.parse(rulesJson);
        if (Array.isArray(parsed)) {
          return parsed.map((rule) => normalizeNodeDraftRule(rule, nodeId));
        }
      } catch (_err) {
        // Fall back to the legacy single-rule attributes below.
      }
    }
    return [
      normalizeNodeDraftRule({
        name: node.getAttribute("data-rule-name"),
        source_signal_id: node.getAttribute("data-rule-source-signal"),
        comparison: node.getAttribute("data-rule-comparison"),
        threshold_value: parseRuleThresholdValue(node.getAttribute("data-rule-threshold-json")),
      }, nodeId),
    ];
  }

  function buildRuleParameterSummary() {
    refreshEditableNodes();
    const totalRules = nodes.reduce((total, node) => total + nodeDraftRules(node).length, 0);
    return {
      total_rules: totalRules,
      touched_nodes: nodes.filter((node) => nodeDraftRulesTouched(node))
        .map((node) => node.getAttribute("data-editable-node-id") || "unknown"),
      truth_effect: "none",
    };
  }

  function nodePortContractTouched(node) {
    return node && node.getAttribute("data-port-contract-touched") === "true";
  }

  function setNodePortContract(node, contract) {
    if (!node) return null;
    const nodeId = node.getAttribute("data-editable-node-id") || "unknown";
    const normalized = normalizePortContract(contract, nodeId);
    node.setAttribute("data-port-input-signal", normalized.input_signal_id);
    node.setAttribute("data-port-output-signal", normalized.output_signal_id);
    node.setAttribute("data-port-value-type", normalized.value_type);
    node.setAttribute("data-port-unit", normalized.unit);
    node.setAttribute("data-port-required", normalized.required ? "true" : "false");
    node.setAttribute("data-port-contract-touched", "true");
    return normalized;
  }

  function nodePortContract(node) {
    if (!node) return normalizePortContract({}, "unknown");
    const nodeId = node.getAttribute("data-editable-node-id") || "unknown";
    return normalizePortContract({
      input_signal_id: node.getAttribute("data-port-input-signal") || nodeId,
      output_signal_id: node.getAttribute("data-port-output-signal") || nodeId,
      value_type: node.getAttribute("data-port-value-type") || "boolean",
      unit: node.getAttribute("data-port-unit") || "",
      required: node.getAttribute("data-port-required") || "false",
      source_ref: "ui_draft.port_contract",
    }, nodeId);
  }

  function portRowsForNodeContract(node) {
    if (!node || !nodePortContractTouched(node)) return [];
    const nodeId = node.getAttribute("data-editable-node-id") || "unknown";
    const contract = nodePortContract(node);
    return [
      {
        id: contract.input_port_id,
        node_id: nodeId,
        direction: "in",
        signal_id: contract.input_signal_id,
        value_type: contract.value_type,
        unit: contract.unit,
        required: contract.required,
        source_ref: contract.source_ref,
        truth_effect: "none",
      },
      {
        id: contract.output_port_id,
        node_id: nodeId,
        direction: "out",
        signal_id: contract.output_signal_id,
        value_type: contract.value_type,
        unit: contract.unit,
        required: contract.required,
        source_ref: contract.source_ref,
        truth_effect: "none",
      },
    ];
  }

  function portHandlePayload(node, direction) {
    if (!node) return null;
    const nodeId = node.getAttribute("data-editable-node-id") || "unknown";
    const contract = nodePortContract(node);
    const isOutput = direction === "out";
    return {
      node_id: nodeId,
      direction: isOutput ? "out" : "in",
      port_id: isOutput ? contract.output_port_id : contract.input_port_id,
      signal_id: isOutput ? contract.output_signal_id : contract.input_signal_id,
      value_type: contract.value_type,
      unit: contract.unit,
      required: contract.required,
      truth_effect: "none",
    };
  }

  function edgePortContract(edge) {
    if (!edge) {
      return {
        source_port_id: "evidence_gap",
        target_port_id: "evidence_gap",
        signal_id: "evidence_gap",
        value_type: "unknown",
        unit: "",
        required: false,
        truth_effect: "none",
      };
    }
    const defaultSourcePortId = edge.source ? `${edge.source}:out` : "evidence_gap";
    const defaultTargetPortId = edgeTargetPortId(edge) || "evidence_gap";
    return {
      source_port_id: normalizedInterfaceField(edge.source_port_id || edge.sourcePortId || defaultSourcePortId),
      target_port_id: normalizedInterfaceField(edge.target_port_id || edge.targetPortId || defaultTargetPortId),
      signal_id: normalizedInterfaceField(edge.signal_id || edge.signalId || `${edge.source || "unknown"}__to__${edge.target || "unknown"}`),
      value_type: normalizePortValueType(edge.value_type || edge.valueType || "boolean"),
      unit: String(edge.unit === null || edge.unit === undefined ? "" : edge.unit).trim(),
      required: normalizePortRequired(edge.required),
      truth_effect: "none",
    };
  }

  function edgeWireLabel(edge) {
    const contract = edgePortContract(edge);
    return normalizedInterfaceField(
      (edge && (edge.edge_label || edge.edgeLabel))
      || `${contract.source_port_id} -> ${contract.target_port_id}`,
    );
  }

  function normalizeEdgeRouteWaypoint(waypoint) {
    if (!waypoint || typeof waypoint !== "object" || Array.isArray(waypoint)) {
      return { x: 0, y: 0 };
    }
    return {
      x: Number.parseFloat(waypoint.x) || 0,
      y: Number.parseFloat(waypoint.y) || 0,
    };
  }

  function normalizeEdgeRouteMetadata(edge, contractRecord) {
    const contract = contractRecord || edgePortContract(edge);
    const routeSource =
      edge && typeof edge === "object" && !Array.isArray(edge)
        ? (edge.route_metadata || edge.routeMetadata || edge.route || {})
        : {};
    const waypoints = Array.isArray(routeSource.waypoints)
      ? routeSource.waypoints.map((waypoint) => normalizeEdgeRouteWaypoint(waypoint))
      : [];
    const routeLabel = normalizedInterfaceField(
      (edge && (edge.edge_label || edge.edgeLabel))
      || routeSource.edge_label
      || routeSource.edgeLabel
      || routeSource.label
      || `${contract.source_port_id} -> ${contract.target_port_id}`,
    );
    return {
      version: edgeRouteMetadataVersion,
      routing_mode: normalizedInterfaceField(routeSource.routing_mode || routeSource.routingMode || "orthogonal"),
      source_node_id: normalizedInterfaceField(edge && edge.source),
      target_node_id: normalizedInterfaceField(edge && edge.target),
      source_port_id: normalizedInterfaceField(contract.source_port_id),
      target_port_id: normalizedInterfaceField(contract.target_port_id),
      edge_label: routeLabel,
      waypoint_count: waypoints.length,
      waypoints,
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    };
  }

  function setEdgePortContract(edge, contract) {
    if (!edge) return null;
    const source = contract && typeof contract === "object" ? contract : {};
    const normalized = edgePortContract({
      ...edge,
      source_port_id: source.source_port_id || source.sourcePortId || edge.source_port_id,
      target_port_id: source.target_port_id || source.targetPortId || edge.target_port_id,
      signal_id: source.signal_id || source.signalId || edge.signal_id,
      value_type: source.value_type || source.valueType || edge.value_type,
      unit: source.unit !== undefined ? source.unit : edge.unit,
      required: source.required !== undefined ? source.required : edge.required,
    });
    edge.source_port_id = normalized.source_port_id;
    edge.target_port_id = normalized.target_port_id;
    edge.signal_id = normalized.signal_id;
    edge.value_type = normalized.value_type;
    edge.unit = normalized.unit;
    edge.required = normalized.required;
    edge.edge_label = edgeWireLabel(edge);
    edge.route_metadata = normalizeEdgeRouteMetadata(edge, normalized);
    return normalized;
  }

  function addUniquePortRow(rows, port) {
    if (!port || !port.id || port.id === "evidence_gap") return;
    if (rows.some((existing) => existing.id === port.id)) return;
    rows.push(port);
  }

  function collectWorkbenchTypedPorts() {
    refreshEditableNodes();
    const rows = [];
    for (const node of nodes) {
      for (const port of portRowsForNodeContract(node)) {
        addUniquePortRow(rows, port);
      }
    }
    for (const edge of draftEdges) {
      const contract = edgePortContract(edge);
      if (contract.source_port_id && contract.source_port_id !== "evidence_gap") {
        addUniquePortRow(rows, {
          id: contract.source_port_id,
          node_id: edge.source || "unknown",
          direction: "out",
          signal_id: contract.signal_id,
          value_type: contract.value_type,
          unit: contract.unit,
          required: contract.required,
          source_ref: `ui_draft.edges.${edge.id || "unknown"}.source_port`,
          truth_effect: "none",
        });
      }
      if (contract.target_port_id && contract.target_port_id !== "evidence_gap") {
        addUniquePortRow(rows, {
          id: contract.target_port_id,
          node_id: edge.target || "unknown",
          direction: "in",
          signal_id: contract.signal_id,
          value_type: contract.value_type,
          unit: contract.unit,
          required: contract.required,
          source_ref: `ui_draft.edges.${edge.id || "unknown"}.target_port`,
          truth_effect: "none",
        });
      }
    }
    return rows;
  }

  function buildPortContractSummary(ports, edges) {
    const typedPorts = ports || [];
    const edgeContracts = (edges || []).filter((edge) => {
      const contract = edgePortContract(edge);
      return contract.source_port_id !== "evidence_gap" && contract.target_port_id !== "evidence_gap";
    });
    return {
      total_ports: typedPorts.length,
      required_ports: typedPorts.filter((port) => port.required === true).length,
      edge_contracts: edgeContracts.length,
      value_types: Array.from(new Set(typedPorts.map((port) => port.value_type))).sort(),
      truth_effect: "none",
    };
  }

  function portRowsById(ports) {
    const result = {};
    for (const port of ports || []) {
      if (port && port.id && !result[port.id]) {
        result[port.id] = port;
      }
    }
    return result;
  }

  function portCompatibilityForEdge(edge, ports) {
    const byId = portRowsById(ports);
    const contract = edgePortContract(edge);
    const source = byId[contract.source_port_id] || null;
    const target = byId[contract.target_port_id] || null;
    const issues = [];
    const edgeId = edge && (edge.id || `${edge.source || "unknown"}->${edge.target || "unknown"}`);
    if (!source) {
      issues.push({
        severity: "error",
        code: "missing_source_port",
        edge_id: edgeId,
        port_id: contract.source_port_id,
        message: `Missing source port ${contract.source_port_id}`,
      });
    } else if (source.direction !== "out") {
      issues.push({
        severity: "error",
        code: "source_direction_not_out",
        edge_id: edgeId,
        port_id: source.id,
        message: `Source port ${source.id} direction is ${source.direction}`,
      });
    }
    if (!target) {
      issues.push({
        severity: "error",
        code: "missing_target_port",
        edge_id: edgeId,
        port_id: contract.target_port_id,
        message: `Missing target port ${contract.target_port_id}`,
      });
    } else if (target.direction !== "in") {
      issues.push({
        severity: "error",
        code: "target_direction_not_in",
        edge_id: edgeId,
        port_id: target.id,
        message: `Target port ${target.id} direction is ${target.direction}`,
      });
    }
    if (source && target) {
      const sourceType = source.value_type || "unknown";
      const targetType = target.value_type || "unknown";
      if (sourceType === "unknown" || targetType === "unknown") {
        issues.push({
          severity: "warning",
          code: "unknown_value_type",
          edge_id: edgeId,
          port_id: `${source.id}->${target.id}`,
          message: `Unknown value type on ${source.id}->${target.id}`,
        });
      } else if (sourceType !== targetType) {
        issues.push({
          severity: "warning",
          code: "value_type_mismatch",
          edge_id: edgeId,
          port_id: `${source.id}->${target.id}`,
          message: `Value type mismatch ${sourceType}->${targetType}`,
        });
      }
    }
    const status = issues.some((issue) => issue.severity === "error")
      ? "fail"
      : (issues.length ? "warn" : "pass");
    return {
      edge_id: edgeId,
      status,
      source_port_id: contract.source_port_id,
      target_port_id: contract.target_port_id,
      source_direction: source ? source.direction : "missing",
      target_direction: target ? target.direction : "missing",
      source_value_type: source ? source.value_type : "missing",
      target_value_type: target ? target.value_type : "missing",
      issues,
      truth_effect: "none",
    };
  }

  function buildPortCompatibilityReport(ports, edges) {
    const edgeReports = (edges || []).map((edge) => portCompatibilityForEdge(edge, ports));
    const issues = edgeReports.flatMap((report) => report.issues);
    const status = issues.some((issue) => issue.severity === "error")
      ? "fail"
      : (issues.length ? "warn" : "pass");
    return {
      kind: "well-harness-workbench-port-compatibility-report",
      version: 1,
      status,
      edge_count: edgeReports.length,
      issue_count: issues.length,
      warning_count: issues.filter((issue) => issue.severity === "warning").length,
      error_count: issues.filter((issue) => issue.severity === "error").length,
      edges: edgeReports,
      issues,
      truth_effect: "none",
    };
  }

  function interfaceMatrixPortMetadata(port) {
    if (!port || typeof port !== "object") {
      return {
        port_id: "evidence_gap",
        node_id: "evidence_gap",
        direction: "evidence_gap",
        signal_id: "evidence_gap",
        value_type: "evidence_gap",
        unit: "",
        required: false,
        source_ref: "evidence_gap",
        truth_effect: "none",
      };
    }
    return {
      port_id: normalizedInterfaceField(port.id),
      node_id: normalizedInterfaceField(port.node_id),
      direction: normalizedInterfaceField(port.direction),
      signal_id: normalizedInterfaceField(port.signal_id),
      value_type: normalizedInterfaceField(port.value_type),
      unit: port.unit === undefined || port.unit === null ? "" : String(port.unit),
      required: port.required === true,
      source_ref: normalizedInterfaceField(port.source_ref),
      truth_effect: "none",
    };
  }

  function diagnosticRuleIdsForInterfaceBinding(binding, diagnostics) {
    const ownerKey = hardwareBindingOwnerKey(binding);
    const interfaceKey = hardwareBindingInterfaceKey(binding);
    const issues = diagnostics && Array.isArray(diagnostics.issues) ? diagnostics.issues : [];
    return Array.from(new Set(issues
      .filter((issue) => issue && (
        issue.target === ownerKey
        || issue.issue_target === ownerKey
        || issue.target === interfaceKey
        || issue.issue_target === interfaceKey
      ))
      .map((issue) => normalizedInterfaceField(issue.rule_id || "hardware_binding_diagnostic"))));
  }

  function buildInterfaceMatrixRows(bindings, ports, diagnostics) {
    const byPortId = portRowsById(ports || []);
    return (Array.isArray(bindings) ? bindings : []).map((binding, index) => {
      const normalized = normalizeInterfaceBinding(
        binding,
        binding && binding.owner_kind,
        binding && binding.owner_id,
      );
      const quality = interfaceBindingQualityReport(normalized);
      const localPort = interfaceMatrixPortMetadata(byPortId[normalized.port_local]);
      const peerPort = interfaceMatrixPortMetadata(byPortId[normalized.port_peer]);
      const diagnosticRuleIds = diagnosticRuleIdsForInterfaceBinding(normalized, diagnostics);
      return {
        row_id: `interface:${String(index + 1).padStart(2, "0")}:${normalized.owner_kind}:${normalized.owner_id}`,
        owner_kind: normalized.owner_kind,
        owner_id: normalized.owner_id,
        hardware_id: normalized.hardware_id,
        cable: normalized.cable,
        connector: normalized.connector,
        port_local: normalized.port_local,
        port_peer: normalized.port_peer,
        evidence_status: normalized.evidence_status,
        binding_quality: quality.status,
        binding_missing_fields: quality.missing_fields,
        local_typed_port: localPort,
        peer_typed_port: peerPort,
        typed_port_status: localPort.port_id !== "evidence_gap" || peerPort.port_id !== "evidence_gap"
          ? "linked"
          : "evidence_gap",
        diagnostic_issue_count: diagnosticRuleIds.length,
        diagnostic_rule_ids: diagnosticRuleIds,
        source_ref: normalized.source_ref,
        truth_effect: "none",
      };
    });
  }

  function buildWorkbenchInterfaceMatrix(bindings, ports, diagnostics, coverage) {
    const hardwareBindings = Array.isArray(bindings) ? bindings : [];
    const typedPorts = Array.isArray(ports) ? ports : [];
    const bindingDiagnostics = diagnostics || buildHardwareBindingDiagnosticsReport(hardwareBindings);
    const bindingCoverage = coverage || buildInterfaceBindingCoverageSummary(hardwareBindings);
    const rows = buildInterfaceMatrixRows(hardwareBindings, typedPorts, bindingDiagnostics);
    const evidenceGapFieldCount = rows.reduce(
      (total, row) => total + (Array.isArray(row.binding_missing_fields) ? row.binding_missing_fields.length : 0),
      0,
    );
    return {
      kind: "well-harness-workbench-interface-matrix",
      version: 1,
      system_id: "thrust-reverser",
      matrix_scope: "sandbox_candidate_interface_design",
      row_count: rows.length,
      typed_port_count: typedPorts.length,
      evidence_gap_field_count: evidenceGapFieldCount,
      diagnostics_status: bindingDiagnostics.status || "unknown",
      diagnostics_issue_count: bindingDiagnostics.issue_count || 0,
      coverage: {
        total_bindings: bindingCoverage.total_bindings || rows.length,
        complete: bindingCoverage.complete || 0,
        partial: bindingCoverage.partial || 0,
        missing: bindingCoverage.missing || 0,
      },
      rows,
      truth_effect: "none",
    };
  }

  function pushInterfaceMatrixValidationIssue(issues, issue) {
    issues.push({
      severity: "warning",
      row_id: "matrix",
      owner_kind: "matrix",
      owner_id: "matrix",
      suggestion: "Review the pending interface matrix before applying it to the sandbox draft.",
      truth_effect: "none",
      ...issue,
    });
  }

  function finalizeInterfaceMatrixValidationReport(report) {
    const issues = Array.isArray(report.issues) ? report.issues : [];
    const status = issues.some((issue) => issue.severity === "error")
      ? "fail"
      : (issues.length ? "warn" : "pass");
    return {
      ...report,
      status,
      issue_count: issues.length,
      error_count: issues.filter((issue) => issue.severity === "error").length,
      warning_count: issues.filter((issue) => issue.severity !== "error").length,
      truth_effect: "none",
    };
  }

  function emptyInterfaceMatrixValidationReport(status, message) {
    const issues = [];
    if (message) {
      pushInterfaceMatrixValidationIssue(issues, {
        rule_id: "matrix_parse_error",
        severity: "error",
        message,
        suggestion: "Paste a well-formed well-harness-workbench-interface-matrix JSON object.",
      });
    }
    return finalizeInterfaceMatrixValidationReport({
      kind: "well-harness-workbench-interface-matrix-validation-report",
      version: 1,
      report_scope: "pending_interface_matrix_import",
      status: status || "fail",
      matrix_checksum: "unavailable",
      row_count: 0,
      applyable_row_count: 0,
      skipped_row_count: 0,
      changed_row_count: 0,
      noop_row_count: 0,
      malformed_row_count: message ? 1 : 0,
      missing_owner_count: 0,
      evidence_gap_field_count: 0,
      duplicate_interface_reuse_count: 0,
      truth_effect_violation_count: 0,
      typed_port_conflict_count: 0,
      rows: [],
      issues,
      truth_effect: "none",
    });
  }

  function interfaceMatrixOwnerExists(ownerKind, ownerId) {
    refreshEditableNodes();
    if (ownerKind === "node") {
      return nodes.some((candidate) => editableNodeId(candidate) === ownerId);
    }
    if (ownerKind === "edge") {
      return draftEdges.some((candidate) => (
        candidate.id === ownerId
        || `${candidate.source || "unknown"}->${candidate.target || "unknown"}` === ownerId
      ));
    }
    return false;
  }

  const interfaceMatrixDiffFields = [
    "hardware_id",
    "cable",
    "connector",
    "port_local",
    "port_peer",
    "evidence_status",
  ];

  function interfaceMatrixCurrentBinding(ownerKind, ownerId) {
    refreshEditableNodes();
    if (ownerKind === "node") {
      const node = nodes.find((candidate) => editableNodeId(candidate) === ownerId);
      return node ? nodeInterfaceBinding(node) : null;
    }
    if (ownerKind === "edge") {
      const edge = draftEdges.find((candidate) => (
        candidate.id === ownerId
        || `${candidate.source || "unknown"}->${candidate.target || "unknown"}` === ownerId
      ));
      return edge ? edgeInterfaceBinding(edge) : null;
    }
    return null;
  }

  function interfaceMatrixDiffBindingFields(binding) {
    if (!binding || typeof binding !== "object") return null;
    const result = {
      owner_kind: normalizedInterfaceField(binding.owner_kind),
      owner_id: normalizedInterfaceField(binding.owner_id),
      truth_effect: "none",
    };
    for (const fieldName of interfaceMatrixDiffFields) {
      result[fieldName] = normalizedInterfaceField(binding[fieldName]);
    }
    return result;
  }

  function interfaceMatrixBindingDelta(currentBinding, candidateBinding) {
    const current = interfaceMatrixDiffBindingFields(currentBinding);
    const candidate = interfaceMatrixDiffBindingFields(candidateBinding);
    const changedFields = [];
    const fieldDeltas = {};
    if (current && candidate) {
      for (const fieldName of interfaceMatrixDiffFields) {
        if (current[fieldName] === candidate[fieldName]) continue;
        changedFields.push(fieldName);
        fieldDeltas[fieldName] = {
          current: current[fieldName],
          candidate: candidate[fieldName],
          truth_effect: "none",
        };
      }
    }
    return {
      current_binding: current,
      candidate_binding: candidate,
      changed_fields: changedFields,
      field_deltas: fieldDeltas,
      change_count: changedFields.length,
      truth_effect: "none",
    };
  }

  function matrixTypedPortIssueCount(row, rowId, issues) {
    const localPort = row && row.local_typed_port && typeof row.local_typed_port === "object"
      ? row.local_typed_port
      : null;
    const peerPort = row && row.peer_typed_port && typeof row.peer_typed_port === "object"
      ? row.peer_typed_port
      : null;
    const localPortId = localPort ? normalizedInterfaceField(localPort.port_id) : "evidence_gap";
    const peerPortId = peerPort ? normalizedInterfaceField(peerPort.port_id) : "evidence_gap";
    let issueCount = 0;
    if (
      localPort
      && !isInterfaceEvidenceGap(localPortId)
      && normalizedInterfaceField(row.port_local) !== localPortId
    ) {
      issueCount += 1;
      pushInterfaceMatrixValidationIssue(issues, {
        rule_id: "typed_port_metadata_mismatch",
        row_id: rowId,
        owner_kind: normalizedInterfaceField(row.owner_kind),
        owner_id: normalizedInterfaceField(row.owner_id),
        message: `${rowId} port_local does not match local_typed_port.port_id.`,
        suggestion: "Refresh/export the matrix after editing port ids, or update typed-port metadata together.",
      });
    }
    if (
      peerPort
      && !isInterfaceEvidenceGap(peerPortId)
      && normalizedInterfaceField(row.port_peer) !== peerPortId
    ) {
      issueCount += 1;
      pushInterfaceMatrixValidationIssue(issues, {
        rule_id: "typed_port_metadata_mismatch",
        row_id: rowId,
        owner_kind: normalizedInterfaceField(row.owner_kind),
        owner_id: normalizedInterfaceField(row.owner_id),
        message: `${rowId} port_peer does not match peer_typed_port.port_id.`,
        suggestion: "Refresh/export the matrix after editing peer port ids, or update typed-port metadata together.",
      });
    }
    if (localPort && peerPort) {
      const localType = normalizePortValueType(localPort.value_type);
      const peerType = normalizePortValueType(peerPort.value_type);
      if (localType !== "unknown" && peerType !== "unknown" && localType !== peerType) {
        issueCount += 1;
        pushInterfaceMatrixValidationIssue(issues, {
          rule_id: "typed_port_value_type_mismatch",
          row_id: rowId,
          owner_kind: normalizedInterfaceField(row.owner_kind),
          owner_id: normalizedInterfaceField(row.owner_id),
          message: `${rowId} typed-port value mismatch ${localType}->${peerType}.`,
          suggestion: "Check the edge/source-target port contract before applying the matrix.",
        });
      }
    }
    return issueCount;
  }

  function buildInterfaceMatrixValidationReport(payload) {
    if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
      return emptyInterfaceMatrixValidationReport("fail", "interface matrix JSON must be an object");
    }

    const issues = [];
    const rowReports = [];
    const reusableBindings = [];
    let malformedRowCount = 0;
    let missingOwnerCount = 0;
    let evidenceGapFieldCount = 0;
    let truthEffectViolationCount = 0;
    let typedPortConflictCount = 0;
    let changedRowCount = 0;
    let noopRowCount = 0;

    if (payload.kind !== "well-harness-workbench-interface-matrix") {
      malformedRowCount += 1;
      pushInterfaceMatrixValidationIssue(issues, {
        rule_id: "matrix_kind_invalid",
        severity: "error",
        message: "interface matrix kind must be well-harness-workbench-interface-matrix",
      });
    }
    if (payload.version !== 1) {
      malformedRowCount += 1;
      pushInterfaceMatrixValidationIssue(issues, {
        rule_id: "matrix_version_invalid",
        severity: "error",
        message: "interface matrix version must be 1",
      });
    }
    if (payload.truth_effect !== "none") {
      truthEffectViolationCount += 1;
      pushInterfaceMatrixValidationIssue(issues, {
        rule_id: "matrix_truth_effect_violation",
        severity: "error",
        message: "interface matrix truth_effect must be none",
        suggestion: "A sandbox matrix cannot claim certified or DAL truth.",
      });
    }
    if (!Array.isArray(payload.rows)) {
      malformedRowCount += 1;
      pushInterfaceMatrixValidationIssue(issues, {
        rule_id: "matrix_rows_invalid",
        severity: "error",
        message: "interface matrix rows must be an array",
      });
    }

    const rows = Array.isArray(payload.rows) ? payload.rows : [];
    for (let index = 0; index < rows.length; index += 1) {
      const row = rows[index];
      const fallbackRowId = `interface:import:${String(index + 1).padStart(2, "0")}`;
      if (!row || typeof row !== "object" || Array.isArray(row)) {
        malformedRowCount += 1;
        rowReports.push({
          row_id: fallbackRowId,
          owner_kind: "invalid",
          owner_id: "invalid",
          status: "reject",
          action: "none",
          owner_exists: false,
          evidence_gap_fields: [],
          issue_count: 1,
          current_binding: null,
          candidate_binding: null,
          changed_fields: [],
          field_deltas: {},
          change_count: 0,
          truth_effect: "none",
        });
        pushInterfaceMatrixValidationIssue(issues, {
          rule_id: "matrix_row_invalid",
          severity: "error",
          row_id: fallbackRowId,
          owner_kind: "invalid",
          owner_id: "invalid",
          message: `${fallbackRowId} must be an object`,
        });
        continue;
      }

      const rowId = normalizedInterfaceField(row.row_id || fallbackRowId);
      const ownerKind = normalizedInterfaceField(row.owner_kind);
      const ownerId = normalizedInterfaceField(row.owner_id);
      const binding = interfaceBindingFromMatrixRow(row);
      const evidenceGapFields = hardwareBindingEvidenceGapFields(binding);
      const ownerKindValid = ownerKind === "node" || ownerKind === "edge";
      const ownerIdValid = !isInterfaceEvidenceGap(ownerId);
      const ownerExists = ownerKindValid && ownerIdValid && interfaceMatrixOwnerExists(ownerKind, ownerId);
      const rowIssueStart = issues.length;

      if (row.truth_effect !== "none") {
        truthEffectViolationCount += 1;
        pushInterfaceMatrixValidationIssue(issues, {
          rule_id: "row_truth_effect_violation",
          severity: "error",
          row_id: rowId,
          owner_kind: ownerKind,
          owner_id: ownerId,
          message: `${rowId} truth_effect must be none`,
          suggestion: "Remove certified/DAL truth claims from the sandbox matrix before applying.",
        });
      }
      if (!ownerKindValid || !ownerIdValid) {
        malformedRowCount += 1;
        pushInterfaceMatrixValidationIssue(issues, {
          rule_id: "row_owner_invalid",
          severity: "error",
          row_id: rowId,
          owner_kind: ownerKind,
          owner_id: ownerId,
          message: `${rowId} must target owner_kind node|edge and a non-empty owner_id.`,
        });
      } else if (!ownerExists) {
        missingOwnerCount += 1;
        pushInterfaceMatrixValidationIssue(issues, {
          rule_id: "row_owner_missing",
          row_id: rowId,
          owner_kind: ownerKind,
          owner_id: ownerId,
          message: `${rowId} targets missing ${ownerKind}:${ownerId}; it will be skipped.`,
          suggestion: "Create the node/edge first or remove this row from the pending import.",
        });
      }
      evidenceGapFieldCount += evidenceGapFields.length;
      if (evidenceGapFields.length) {
        pushInterfaceMatrixValidationIssue(issues, {
          rule_id: "row_evidence_gap",
          row_id: rowId,
          owner_kind: ownerKind,
          owner_id: ownerId,
          message: `${rowId} has ${evidenceGapFields.length} evidence-gap field(s): ${evidenceGapFields.join(", ")}`,
          suggestion: "Leave explicit evidence_gap values if source data is missing; do not invent certified hardware data.",
        });
      }
      typedPortConflictCount += matrixTypedPortIssueCount(row, rowId, issues);
      reusableBindings.push({ binding, row_id: rowId });

      const rowHasError = issues.slice(rowIssueStart).some((issue) => issue.severity === "error");
      const delta = rowHasError
        ? interfaceMatrixBindingDelta(null, null)
        : interfaceMatrixBindingDelta(
          ownerExists ? interfaceMatrixCurrentBinding(ownerKind, ownerId) : null,
          binding,
        );
      if (!rowHasError && ownerExists) {
        if (delta.change_count > 0) changedRowCount += 1;
        else noopRowCount += 1;
      }
      const status = rowHasError
        ? "reject"
        : (!ownerExists ? "skipped" : (delta.change_count > 0 ? "applyable" : "no_op"));
      const action = rowHasError
        ? "none"
        : (!ownerExists ? "skip" : (delta.change_count > 0 ? "apply" : "none"));
      rowReports.push({
        row_id: rowId,
        owner_kind: ownerKind,
        owner_id: ownerId,
        status,
        action,
        owner_exists: ownerExists,
        evidence_gap_fields: evidenceGapFields,
        issue_count: issues.length - rowIssueStart,
        current_binding: delta.current_binding,
        candidate_binding: delta.candidate_binding,
        changed_fields: delta.changed_fields,
        field_deltas: delta.field_deltas,
        change_count: delta.change_count,
        binding_quality: binding.binding_quality,
        truth_effect: "none",
      });
    }

    const interfaceKeyGroups = new Map();
    for (const item of reusableBindings) {
      const interfaceKey = hardwareBindingInterfaceKey(item.binding);
      if (!interfaceKey) continue;
      if (!interfaceKeyGroups.has(interfaceKey)) interfaceKeyGroups.set(interfaceKey, []);
      interfaceKeyGroups.get(interfaceKey).push(item);
    }
    let duplicateInterfaceReuseCount = 0;
    for (const [interfaceKey, grouped] of interfaceKeyGroups.entries()) {
      const owners = Array.from(new Set(grouped.map((item) => hardwareBindingOwnerKey(item.binding))));
      if (owners.length <= 1) continue;
      duplicateInterfaceReuseCount += 1;
      pushInterfaceMatrixValidationIssue(issues, {
        rule_id: "connector_port_reuse",
        row_id: grouped.map((item) => item.row_id).join(","),
        owner_kind: "mixed",
        owner_id: owners.join(","),
        message: `Connector/port reuse detected for ${interfaceKey}.`,
        suggestion: "Verify shared hardware interface reuse is intentional before applying.",
        evidence_refs: grouped.map((item) => item.row_id),
      });
    }

    return finalizeInterfaceMatrixValidationReport({
      kind: "well-harness-workbench-interface-matrix-validation-report",
      version: 1,
      report_scope: "pending_interface_matrix_import",
      matrix_checksum: checksumEvidenceArchiveField(payload),
      matrix_kind: normalizedInterfaceField(payload.kind),
      row_count: rows.length,
      applyable_row_count: rowReports.filter((row) => row.status === "applyable").length,
      skipped_row_count: rowReports.filter((row) => row.status === "skipped").length,
      changed_row_count: changedRowCount,
      noop_row_count: noopRowCount,
      malformed_row_count: malformedRowCount,
      missing_owner_count: missingOwnerCount,
      evidence_gap_field_count: evidenceGapFieldCount,
      duplicate_interface_reuse_count: duplicateInterfaceReuseCount,
      truth_effect_violation_count: truthEffectViolationCount,
      typed_port_conflict_count: typedPortConflictCount,
      rows: rowReports,
      issues,
      truth_effect: "none",
    });
  }

  function interfaceMatrixValidationSummary(report) {
    const source = report && typeof report === "object" ? report : null;
    return {
      status: source ? source.status : "not_run",
      row_count: source ? source.row_count || 0 : 0,
      applyable_row_count: source ? source.applyable_row_count || 0 : 0,
      skipped_row_count: source ? source.skipped_row_count || 0 : 0,
      changed_row_count: source ? source.changed_row_count || 0 : 0,
      noop_row_count: source ? source.noop_row_count || 0 : 0,
      issue_count: source ? source.issue_count || 0 : 0,
      evidence_gap_field_count: source ? source.evidence_gap_field_count || 0 : 0,
      duplicate_interface_reuse_count: source ? source.duplicate_interface_reuse_count || 0 : 0,
      truth_effect_violation_count: source ? source.truth_effect_violation_count || 0 : 0,
      typed_port_conflict_count: source ? source.typed_port_conflict_count || 0 : 0,
      checksum: source ? checksumEvidenceArchiveField(source) : "not_run",
      truth_effect: "none",
    };
  }

  function matrixReviewBindingValue(binding, fieldName) {
    if (!binding || typeof binding !== "object") return "evidence_gap";
    return normalizedInterfaceField(binding[fieldName]);
  }

  function matrixReviewDeltaText(row) {
    const fields = row && Array.isArray(row.changed_fields) ? row.changed_fields : [];
    if (!fields.length) return "none";
    const current = row.current_binding || null;
    const candidate = row.candidate_binding || null;
    return fields.map((fieldName) => (
      `${fieldName}: ${matrixReviewBindingValue(current, fieldName)} -> ${matrixReviewBindingValue(candidate, fieldName)}`
    )).join("; ");
  }

  function appendMatrixReviewCell(rowEl, text, className) {
    const cell = document.createElement("td");
    if (className) cell.className = className;
    cell.textContent = text;
    rowEl.appendChild(cell);
    return cell;
  }

  function interfaceMatrixSelectedApplyRowIdsFromReview() {
    if (!interfaceMatrixReview) return null;
    const inputs = Array.from(interfaceMatrixReview.querySelectorAll('[data-interface-matrix-review-select="true"]'));
    const selectable = inputs.filter((input) => !input.disabled);
    if (!selectable.length) return null;
    return new Set(selectable
      .filter((input) => input.checked)
      .map((input) => normalizedInterfaceField(input.getAttribute("data-interface-matrix-review-row-id"))));
  }

  function appendMatrixReviewSelectionCell(rowEl, row, selectedRowIds) {
    const cell = document.createElement("td");
    cell.className = "workbench-interface-matrix-review-select-cell";
    const rowId = normalizedInterfaceField(row.row_id);
    const rowStatus = normalizedInterfaceField(row.status);
    const rowAction = normalizedInterfaceField(row.action || "none");
    const canApply = rowStatus === "applyable" && rowAction === "apply";
    const input = document.createElement("input");
    input.type = "checkbox";
    input.setAttribute("data-interface-matrix-review-select", "true");
    input.setAttribute("data-interface-matrix-review-row-id", rowId);
    input.setAttribute("aria-label", `Apply ${rowId}`);
    input.disabled = !canApply;
    input.checked = canApply && (!selectedRowIds || selectedRowIds.has(rowId));
    rowEl.setAttribute("data-row-selected", input.checked ? "true" : "false");
    input.addEventListener("change", () => {
      rowEl.setAttribute("data-row-selected", input.checked ? "true" : "false");
    });
    cell.appendChild(input);
    rowEl.appendChild(cell);
    return cell;
  }

  function renderInterfaceMatrixReviewTable(report, options) {
    if (!interfaceMatrixReview) return;
    interfaceMatrixReview.innerHTML = "";
    const state = report && typeof report === "object" ? normalizedInterfaceField(report.status) : "empty";
    interfaceMatrixReview.setAttribute("data-review-state", state);
    const selectedRowIds = options && options.selectedRowIds instanceof Set
      ? options.selectedRowIds
      : null;

    const summary = document.createElement("p");
    summary.className = "workbench-interface-matrix-review-summary";
    if (!report) {
      summary.textContent = "No matrix validation run yet.";
      interfaceMatrixReview.appendChild(summary);
      return;
    }
    summary.textContent =
      `Review ${state}: ${report.applyable_row_count || 0} applyable, ${report.noop_row_count || 0} no-op, ${report.skipped_row_count || 0} skipped, ${report.issue_count || 0} issue(s).`;
    interfaceMatrixReview.appendChild(summary);

    const rows = Array.isArray(report.rows) ? report.rows : [];
    if (!rows.length) {
      const empty = document.createElement("p");
      empty.className = "workbench-interface-matrix-review-empty";
      empty.textContent = report.issue_count
        ? "Matrix-level validation issue. No row preview is available."
        : "Matrix has no rows to review.";
      interfaceMatrixReview.appendChild(empty);
      return;
    }

    const tableWrap = document.createElement("div");
    tableWrap.className = "workbench-interface-matrix-review-table-wrap";
    const table = document.createElement("table");
    table.className = "workbench-interface-matrix-review-table";
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    ["Apply", "Row", "Owner", "Status", "Action", "Changes", "Delta"].forEach((label) => {
      const th = document.createElement("th");
      th.textContent = label;
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    for (const row of rows) {
      const rowEl = document.createElement("tr");
      const rowStatus = normalizedInterfaceField(row.status);
      const rowAction = normalizedInterfaceField(row.action || "none");
      rowEl.setAttribute("data-row-status", rowStatus);
      rowEl.setAttribute("data-row-action", rowAction);
      rowEl.setAttribute("data-interface-matrix-review-row-id", normalizedInterfaceField(row.row_id));
      rowEl.setAttribute("data-interface-matrix-review-owner-kind", normalizedInterfaceField(row.owner_kind));
      rowEl.setAttribute("data-interface-matrix-review-owner-id", normalizedInterfaceField(row.owner_id));

      appendMatrixReviewSelectionCell(rowEl, row, selectedRowIds);
      appendMatrixReviewCell(rowEl, normalizedInterfaceField(row.row_id), "workbench-interface-matrix-review-row-id");
      appendMatrixReviewCell(
        rowEl,
        `${normalizedInterfaceField(row.owner_kind)}:${normalizedInterfaceField(row.owner_id)}`,
        "workbench-interface-matrix-review-owner",
      );
      appendMatrixReviewCell(rowEl, rowStatus, "workbench-interface-matrix-review-status");
      appendMatrixReviewCell(rowEl, rowAction, "workbench-interface-matrix-review-action");
      appendMatrixReviewCell(
        rowEl,
        `${row.change_count || 0} · ${(Array.isArray(row.changed_fields) && row.changed_fields.length) ? row.changed_fields.join(", ") : "none"}`,
        "workbench-interface-matrix-review-changes",
      );
      appendMatrixReviewCell(rowEl, matrixReviewDeltaText(row), "workbench-interface-matrix-review-delta");
      tbody.appendChild(rowEl);
    }
    table.appendChild(tbody);
    tableWrap.appendChild(table);
    interfaceMatrixReview.appendChild(tableWrap);
  }

  function renderInterfaceMatrixValidationReport(report, options) {
    lastInterfaceMatrixValidationReport = report || null;
    if (interfaceMatrixValidationOutput) {
      interfaceMatrixValidationOutput.value = report ? JSON.stringify(report, null, 2) : "";
    }
    renderInterfaceMatrixReviewTable(report, options);
    if ((!options || options.updateStatus !== false) && interfaceMatrixStatus && report) {
      interfaceMatrixStatus.textContent =
        `Matrix validation ${report.status}: ${report.applyable_row_count || 0} applyable, ${report.skipped_row_count || 0} skipped, ${report.noop_row_count || 0} no-op, ${report.issue_count || 0} issue(s). Truth effect: none.`;
    }
    return report;
  }

  function clearInterfaceMatrixValidationReport(message) {
    lastInterfaceMatrixValidationReport = null;
    if (interfaceMatrixValidationOutput) interfaceMatrixValidationOutput.value = "";
    renderInterfaceMatrixReviewTable(null);
    if (message && interfaceMatrixStatus) {
      interfaceMatrixStatus.textContent = message;
    }
  }

  function validateWorkbenchInterfaceMatrix(options) {
    if (!interfaceMatrixOutput) return null;
    let report = null;
    try {
      const payload = JSON.parse(interfaceMatrixOutput.value || "{}");
      report = buildInterfaceMatrixValidationReport(payload);
    } catch (err) {
      report = emptyInterfaceMatrixValidationReport(
        "fail",
        err && err.message ? err.message : "interface matrix JSON parse failed",
      );
    }
    return renderInterfaceMatrixValidationReport(report, options);
  }

  function selectedNodePayload() {
    if (!selectedNode) return null;
    const nodeId = selectedNode.getAttribute("data-editable-node-id") || "";
    const subsystemGroup = nodeSubsystemMetadata(selectedNode);
    const payload = {
      id: nodeId,
      label: selectedNode.getAttribute("data-node-label") || "",
      op: selectedNode.getAttribute("data-node-op") || "and",
      ruleCount: selectedNode.getAttribute("data-rule-count") || "0",
      evidence: selectedNode.getAttribute("data-hardware-evidence") || "evidence_gap",
      sourceRef: selectedNode.getAttribute("data-source-ref") || "unknown",
      op_catalog_entry: selectedNode.getAttribute("data-op-catalog-entry")
        || selectedNode.getAttribute("data-node-op")
        || "and",
      op_catalog_version: editableOperationCatalogVersion,
      hardware_binding: nodeInterfaceBinding(selectedNode),
    };
    if (subsystemGroup) {
      payload.subsystem_group = subsystemGroup;
    }
    if (nodePortContractTouched(selectedNode)) {
      payload.port_contract = nodePortContract(selectedNode);
    }
    if (nodeDraftRulesTouched(selectedNode)) {
      payload.rules = nodeDraftRules(selectedNode);
    }
    return payload;
  }

  function refreshEditableNodes() {
    nodes = Array.from(shell.querySelectorAll("[data-editable-node-id]"));
  }

  function editableNodeId(node) {
    return node && (node.getAttribute("data-editable-node-id") || "");
  }

  function syncEditableNodeSelectionAttributes() {
    refreshEditableNodes();
    const selectedCount = selectedNodeIds.size;
    for (const node of nodes) {
      const nodeId = editableNodeId(node);
      const isSelected = selectedNodeIds.has(nodeId);
      node.setAttribute("aria-pressed", isSelected ? "true" : "false");
      node.setAttribute("data-multi-selected", isSelected && selectedCount > 1 ? "true" : "false");
    }
    renderCanvasInteractionStatus();
  }

  function setSingleEditableNodeSelection(node) {
    selectedNode = node || null;
    selectedNodeIds = new Set();
    const nodeId = editableNodeId(selectedNode);
    if (nodeId) selectedNodeIds.add(nodeId);
    syncEditableNodeSelectionAttributes();
  }

  function toggleEditableNodeSelection(node) {
    const nodeId = editableNodeId(node);
    if (!nodeId) return;
    if (selectedNodeIds.has(nodeId) && selectedNodeIds.size > 1) {
      selectedNodeIds.delete(nodeId);
    } else {
      selectedNodeIds.add(nodeId);
    }
    selectedNode = node;
    if (!selectedNodeIds.size) selectedNodeIds.add(nodeId);
    syncEditableNodeSelectionAttributes();
  }

  function selectedEditableDraftNodes() {
    refreshEditableNodes();
    const selectedIds = selectedNodeIds.size
      ? selectedNodeIds
      : new Set(selectedNode ? [editableNodeId(selectedNode)] : []);
    return nodes.filter((node) => (
      selectedIds.has(editableNodeId(node))
      && node.getAttribute("data-draft-node") === "true"
    ));
  }

  function clampViewportScale(value) {
    const numeric = Number.parseFloat(value);
    if (!Number.isFinite(numeric)) return 1;
    return Math.max(viewportScaleBounds.min, Math.min(viewportScaleBounds.max, numeric));
  }

  function defaultViewportState() {
    return { scale: 1, panX: 0, panY: 0 };
  }

  function viewportStateSnapshot() {
    return {
      scale: Number(viewportState.scale.toFixed(4)),
      pan_x: Math.round(viewportState.panX),
      pan_y: Math.round(viewportState.panY),
      truth_effect: "none",
      coordinate_effect: "viewport_only",
    };
  }

  function viewportStatusText(actionName) {
    const snapshot = viewportStateSnapshot();
    return `Viewport ${actionName}: zoom ${snapshot.scale} pan ${snapshot.pan_x},${snapshot.pan_y}. Truth effect: none.`;
  }

  function applyViewportTransform(actionName, options) {
    if (!canvas) return viewportStateSnapshot();
    const shouldPersist = !options || options.persist !== false;
    viewportState.scale = clampViewportScale(viewportState.scale);
    canvas.style.setProperty("--viewport-scale", String(viewportState.scale));
    canvas.style.setProperty("--viewport-pan-x", `${viewportState.panX}px`);
    canvas.style.setProperty("--viewport-pan-y", `${viewportState.panY}px`);
    canvas.setAttribute("data-viewport-scale", viewportState.scale.toFixed(4));
    canvas.setAttribute("data-viewport-pan-x", String(Math.round(viewportState.panX)));
    canvas.setAttribute("data-viewport-pan-y", String(Math.round(viewportState.panY)));
    canvas.setAttribute(
      "data-viewport-state",
      viewportState.scale === 1 && viewportState.panX === 0 && viewportState.panY === 0
        ? "reset"
        : "transformed",
    );
    if (actionName && graphValidationStatus) {
      graphValidationStatus.textContent = viewportStatusText(actionName);
    }
    if (shouldPersist) persistDraft();
    return viewportStateSnapshot();
  }

  function setViewportState(nextState, actionName) {
    const state = nextState && typeof nextState === "object" ? nextState : defaultViewportState();
    const fallback = defaultViewportState();
    viewportState.scale = Number.isFinite(Number(state.scale))
      ? clampViewportScale(state.scale)
      : fallback.scale;
    viewportState.panX = Number.isFinite(Number(state.panX)) ? Number(state.panX) : fallback.panX;
    viewportState.panY = Number.isFinite(Number(state.panY)) ? Number(state.panY) : fallback.panY;
    return applyViewportTransform(actionName);
  }

  function resetViewport() {
    return setViewportState({ scale: 1, panX: 0, panY: 0 }, "reset");
  }

  function zoomViewportAt(factor, anchor, actionName) {
    if (!canvas) return viewportStateSnapshot();
    const rect = canvas.getBoundingClientRect();
    const anchorPoint = anchor || { x: rect.width / 2, y: rect.height / 2 };
    const oldScale = viewportState.scale || 1;
    const nextScale = clampViewportScale(oldScale * factor);
    const worldX = (anchorPoint.x - viewportState.panX) / oldScale;
    const worldY = (anchorPoint.y - viewportState.panY) / oldScale;
    viewportState.scale = nextScale;
    viewportState.panX = anchorPoint.x - worldX * nextScale;
    viewportState.panY = anchorPoint.y - worldY * nextScale;
    return applyViewportTransform(actionName || "zoom");
  }

  function canvasViewportPoint(event) {
    if (!canvas || !event) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
  }

  function selectedNodesForViewportFit() {
    refreshEditableNodes();
    const selectedIds = selectedNodeIds.size ? selectedNodeIds : new Set();
    const selected = nodes.filter((node) => selectedIds.has(editableNodeId(node)));
    return selected.length ? selected : nodes;
  }

  function fitViewportToSelection() {
    if (!canvas) return viewportStateSnapshot();
    const fitNodes = selectedNodesForViewportFit();
    if (!fitNodes.length) return viewportStateSnapshot();
    const rect = canvas.getBoundingClientRect();
    const positions = fitNodes.map((node) => editableNodePosition(node));
    const minX = Math.min(...positions.map((position) => position.x));
    const maxX = Math.max(...positions.map((position) => position.x));
    const minY = Math.min(...positions.map((position) => position.y));
    const maxY = Math.max(...positions.map((position) => position.y));
    const widthPx = Math.max(120, ((maxX - minX) / 100) * rect.width);
    const heightPx = Math.max(90, ((maxY - minY) / 100) * rect.height);
    const paddingPx = 96;
    const scale = clampViewportScale(Math.min(
      (rect.width - paddingPx) / widthPx,
      (rect.height - paddingPx) / heightPx,
    ));
    const centerX = ((minX + maxX) / 2 / 100) * rect.width;
    const centerY = ((minY + maxY) / 2 / 100) * rect.height;
    viewportState.scale = scale;
    viewportState.panX = rect.width / 2 - centerX * scale;
    viewportState.panY = rect.height / 2 - centerY * scale;
    return applyViewportTransform(`fit ${fitNodes.length} node(s)`);
  }

  function beginViewportPan(event) {
    if (!canvas || !event) return false;
    if (!(event.button === 1 || spacePanActive)) return false;
    viewportPanState = {
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      panX: viewportState.panX,
      panY: viewportState.panY,
    };
    canvas.setPointerCapture(event.pointerId);
    canvas.setAttribute("data-viewport-panning", "true");
    event.preventDefault();
    return true;
  }

  function pointerEventMatchesState(event, state) {
    if (!event || !state) return false;
    const eventPointerId = Number(event.pointerId);
    const statePointerId = Number(state.pointerId);
    return !(
      Number.isFinite(eventPointerId)
      && Number.isFinite(statePointerId)
      && eventPointerId !== statePointerId
    );
  }

  function updateViewportPan(event) {
    if (!viewportPanState || !pointerEventMatchesState(event, viewportPanState)) return false;
    viewportState.panX = viewportPanState.panX + (event.clientX - viewportPanState.startX);
    viewportState.panY = viewportPanState.panY + (event.clientY - viewportPanState.startY);
    applyViewportTransform("pan", { persist: false });
    event.preventDefault();
    return true;
  }

  function clearViewportPanState(actionName) {
    if (!viewportPanState) return;
    viewportPanState = null;
    if (canvas) canvas.removeAttribute("data-viewport-panning");
    applyViewportTransform(actionName || "pan complete");
  }

  function endViewportPan(event) {
    if (!viewportPanState || !pointerEventMatchesState(event, viewportPanState)) return false;
    clearViewportPanState("pan complete");
    event.preventDefault();
    return true;
  }

  function clampCanvasPercent(value) {
    const numeric = Number.parseFloat(value);
    if (!Number.isFinite(numeric)) return 50;
    return Math.max(4, Math.min(96, numeric));
  }

  function formatCanvasPercent(value) {
    return `${clampCanvasPercent(value).toFixed(2)}%`;
  }

  function canvasPointPercent(event) {
    if (!canvas || !event) return { x: 50, y: 50 };
    const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return { x: 50, y: 50 };
    const rawX = (event.clientX - rect.left - viewportState.panX) / viewportState.scale;
    const rawY = (event.clientY - rect.top - viewportState.panY) / viewportState.scale;
    return {
      x: clampCanvasPercent((rawX / rect.width) * 100),
      y: clampCanvasPercent((rawY / rect.height) * 100),
    };
  }

  function setEditableNodePosition(node, x, y) {
    if (!node) return;
    node.style.setProperty("--node-x", formatCanvasPercent(x));
    node.style.setProperty("--node-y", formatCanvasPercent(y));
  }

  function isSelectionModifier(event) {
    return Boolean(event && (event.shiftKey || event.metaKey || event.ctrlKey));
  }

  function ensureSelectionMarquee() {
    if (!canvas) return null;
    if (!selectionMarquee) {
      selectionMarquee = document.createElement("div");
      selectionMarquee.className = "workbench-selection-marquee";
      selectionMarquee.setAttribute("aria-hidden", "true");
      canvas.appendChild(selectionMarquee);
    }
    return selectionMarquee;
  }

  function setSelectionMarqueeRect(rect) {
    const marquee = ensureSelectionMarquee();
    if (!marquee || !rect) return;
    marquee.style.setProperty("--marquee-left", `${rect.left}%`);
    marquee.style.setProperty("--marquee-top", `${rect.top}%`);
    marquee.style.setProperty("--marquee-width", `${rect.width}%`);
    marquee.style.setProperty("--marquee-height", `${rect.height}%`);
    marquee.setAttribute("data-active", "true");
  }

  function hideSelectionMarquee() {
    if (selectionMarquee) selectionMarquee.setAttribute("data-active", "false");
  }

  function lassoRectFromPoints(start, current) {
    const left = Math.min(start.x, current.x);
    const right = Math.max(start.x, current.x);
    const top = Math.min(start.y, current.y);
    const bottom = Math.max(start.y, current.y);
    return {
      left,
      right,
      top,
      bottom,
      width: right - left,
      height: bottom - top,
    };
  }

  function lassoNodesWithinRect(rect) {
    if (!rect) return [];
    refreshEditableNodes();
    return nodes.filter((node) => {
      const position = editableNodePosition(node);
      return (
        position.x >= rect.left
        && position.x <= rect.right
        && position.y >= rect.top
        && position.y <= rect.bottom
      );
    });
  }

  function applyLassoSelection(matchedNodes, additive) {
    const matches = Array.isArray(matchedNodes) ? matchedNodes : [];
    if (!additive) selectedNodeIds = new Set();
    for (const node of matches) {
      const nodeId = editableNodeId(node);
      if (nodeId) selectedNodeIds.add(nodeId);
    }
    if (matches.length) {
      selectedNode = matches[matches.length - 1];
    } else if (!additive && selectedNodeIds.size === 0) {
      selectedNode = null;
    }
    selectedEdge = null;
    syncEditableNodeSelectionAttributes();
    if (edgeSvg) {
      for (const path of Array.from(edgeSvg.querySelectorAll("[data-editable-edge-id]"))) {
        path.setAttribute("aria-pressed", "false");
      }
    }
    renderInspector();
    validateEditableGraph();
    updateEditableDraftHash();
    persistDraft();
    if (graphValidationStatus) {
      const draftCount = matches.filter((node) => node.getAttribute("data-draft-node") === "true").length;
      graphValidationStatus.textContent =
        `Graph validation: lasso selected ${matches.length} node(s), ${draftCount} draft movable. Truth effect: none.`;
    }
  }

  function normalizeSubsystemGroupName(value, fallbackIndex) {
    const text = String(value === null || value === undefined ? "" : value).trim();
    return text || `Draft subsystem ${fallbackIndex || 1}`;
  }

  function normalizeSubsystemInterfaceDirection(value) {
    const text = String(value === null || value === undefined ? "" : value).trim().toLowerCase();
    if (["output", "out"].includes(text)) return "output";
    return "input";
  }

  function normalizeSubsystemInterfaceContractRecord(record, groupId, fallbackIndex) {
    if (!record || typeof record !== "object" || Array.isArray(record)) return null;
    const normalizedGroupId = normalizePortField(
      groupId || record.group_id || record.groupId,
      "evidence_gap",
    );
    const direction = normalizeSubsystemInterfaceDirection(record.direction || record.port_direction || record.portDirection);
    const index = Number.parseInt(record.port_index || record.portIndex || fallbackIndex || "1", 10) || 1;
    const label = normalizePortField(record.label || record.port_label || record.portLabel, `Boundary ${direction} ${index}`);
    const id = normalizePortField(
      record.id || record.port_id || record.portId,
      `${normalizedGroupId}:${direction}:${index}`,
    );
    return {
      id,
      group_id: normalizedGroupId,
      direction,
      port_index: index,
      label,
      signal_id: normalizePortField(record.signal_id || record.signalId, "evidence_gap"),
      value_type: normalizePortValueType(record.value_type || record.valueType || "unknown"),
      unit: String(record.unit === null || record.unit === undefined ? "" : record.unit).trim(),
      evidence_status: normalizeEvidenceStatus(record.evidence_status || record.evidenceStatus),
      source_ref: normalizePortField(
        record.source_ref || record.sourceRef,
        `ui_draft.subsystem_interface.${normalizedGroupId}.${direction}.${index}`,
      ),
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    };
  }

  function normalizeSubsystemInterfaceContracts(records, groupId) {
    const normalized = [];
    const usedIds = new Set();
    for (const record of Array.isArray(records) ? records : []) {
      const port = normalizeSubsystemInterfaceContractRecord(record, groupId, normalized.length + 1);
      if (!port || usedIds.has(port.id)) continue;
      usedIds.add(port.id);
      normalized.push(port);
    }
    return normalized;
  }

  function normalizeSubsystemGroupRecord(record, fallbackIndex) {
    if (!record || typeof record !== "object" || Array.isArray(record)) return null;
    const id = String(record.id || record.group_id || record.groupId || `subsystem_${fallbackIndex || 1}`).trim();
    if (!id) return null;
    const nodeIds = Array.isArray(record.node_ids || record.nodeIds)
      ? record.node_ids || record.nodeIds
      : [];
    const uniqueNodeIds = [];
    for (const nodeId of nodeIds) {
      const normalized = String(nodeId || "").trim();
      if (normalized && uniqueNodeIds.indexOf(normalized) === -1) uniqueNodeIds.push(normalized);
    }
    return {
      id,
      name: normalizeSubsystemGroupName(record.name || record.label, fallbackIndex),
      node_ids: uniqueNodeIds,
      created_at: String(record.created_at || record.createdAt || "browser_local_draft"),
      interface_contracts: normalizeSubsystemInterfaceContracts(
        record.interface_contracts || record.interfaceContracts || record.boundary_ports || record.boundaryPorts || [],
        id,
      ),
      candidate_state: "sandbox_candidate",
      source_ref: String(record.source_ref || record.sourceRef || `ui_draft.subsystem_group.${id}`),
      truth_effect: "none",
    };
  }

  function normalizeSubsystemGroups(records) {
    const normalized = [];
    const usedIds = new Set();
    for (const record of Array.isArray(records) ? records : []) {
      const group = normalizeSubsystemGroupRecord(record, normalized.length + 1);
      if (!group || usedIds.has(group.id)) continue;
      usedIds.add(group.id);
      normalized.push(group);
    }
    return normalized;
  }

  function subsystemGroupById(groupId) {
    const id = String(groupId || "").trim();
    return subsystemGroups.find((group) => group.id === id) || null;
  }

  function nodeSubsystemMetadata(node) {
    const groupId = node && node.getAttribute("data-subsystem-id");
    if (!groupId) return null;
    const group = subsystemGroupById(groupId);
    return {
      group_id: groupId,
      name: group ? group.name : node.getAttribute("data-subsystem-label") || groupId,
      source_ref: group ? group.source_ref : `ui_draft.subsystem_group.${groupId}`,
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    };
  }

  function clearNodeSubsystemMetadata(node) {
    if (!node) return;
    node.removeAttribute("data-subsystem-id");
    node.removeAttribute("data-subsystem-label");
  }

  function setNodeSubsystemMetadata(node, metadata) {
    if (!node || !metadata || typeof metadata !== "object") {
      clearNodeSubsystemMetadata(node);
      return;
    }
    const groupId = String(metadata.group_id || metadata.groupId || metadata.id || "").trim();
    if (!groupId) {
      clearNodeSubsystemMetadata(node);
      return;
    }
    const group = subsystemGroupById(groupId);
    node.setAttribute("data-subsystem-id", groupId);
    node.setAttribute(
      "data-subsystem-label",
      group ? group.name : String(metadata.name || metadata.label || groupId),
    );
  }

  function subsystemGroupsFromNodeStates(nodeStates) {
    const groupsById = new Map();
    for (const nodeState of Array.isArray(nodeStates) ? nodeStates : []) {
      if (!nodeState || typeof nodeState !== "object") continue;
      const metadata = nodeState.subsystem_group || nodeState.subsystemGroup;
      if (!metadata || typeof metadata !== "object") continue;
      const groupId = String(metadata.group_id || metadata.groupId || metadata.id || "").trim();
      const nodeId = String(nodeState.id || "").trim();
      if (!groupId || !nodeId) continue;
      const existing = groupsById.get(groupId) || {
        id: groupId,
        name: metadata.name || metadata.label || groupId,
        node_ids: [],
        source_ref: metadata.source_ref || metadata.sourceRef || `ui_draft.subsystem_group.${groupId}`,
        truth_effect: "none",
      };
      if (existing.node_ids.indexOf(nodeId) === -1) existing.node_ids.push(nodeId);
      groupsById.set(groupId, existing);
    }
    return Array.from(groupsById.values());
  }

  function syncSubsystemNodeAttributes() {
    refreshEditableNodes();
    const draftNodeIds = new Set(
      nodes
        .filter((node) => node.getAttribute("data-draft-node") === "true")
        .map((node) => editableNodeId(node))
        .filter(Boolean),
    );
    const normalizedGroups = normalizeSubsystemGroups(subsystemGroups)
      .map((group) => ({
        ...group,
        node_ids: group.node_ids
          .filter((nodeId) => draftNodeIds.has(nodeId))
          .filter((nodeId, index, all) => all.indexOf(nodeId) === index),
      }))
      .filter((group) => group.node_ids.length > 0);
    const membership = new Map();
    for (const group of normalizedGroups) {
      for (const nodeId of group.node_ids) membership.set(nodeId, group);
    }
    subsystemGroups = normalizedGroups;
    for (const node of nodes) {
      const group = membership.get(editableNodeId(node));
      if (group) {
        setNodeSubsystemMetadata(node, { group_id: group.id, name: group.name });
      } else {
        clearNodeSubsystemMetadata(node);
      }
    }
    return subsystemGroups;
  }

  function selectedSubsystemGroup() {
    const selectedDraftNodes = selectedEditableDraftNodes();
    const selectedGroupIds = selectedDraftNodes
      .map((node) => node.getAttribute("data-subsystem-id") || "")
      .filter(Boolean);
    const activeNodeGroupId = selectedNode && selectedNode.getAttribute("data-subsystem-id");
    const groupId = activeNodeGroupId || selectedGroupIds[0] || "";
    return subsystemGroupById(groupId);
  }

  function subsystemGroupsSnapshot() {
    return syncSubsystemNodeAttributes().map((group) => ({
      ...group,
      node_ids: [...group.node_ids],
      interface_contracts: normalizeSubsystemInterfaceContracts(group.interface_contracts || [], group.id),
    }));
  }

  function buildSubsystemInterfaceContractsSummary(groups) {
    const sourceGroups = Array.isArray(groups) ? groups : subsystemGroupsSnapshot();
    const contractGroups = sourceGroups.map((group) => ({
      group_id: group.id,
      group_name: group.name,
      node_ids: Array.isArray(group.node_ids) ? [...group.node_ids] : [],
      port_count: Array.isArray(group.interface_contracts) ? group.interface_contracts.length : 0,
      interface_contracts: normalizeSubsystemInterfaceContracts(group.interface_contracts || [], group.id),
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    }));
    return {
      kind: "well-harness-workbench-subsystem-interface-contracts",
      version: 1,
      system_id: "thrust-reverser",
      contract_scope: "sandbox_subsystem_boundary_ports",
      group_count: contractGroups.length,
      port_count: contractGroups.reduce((total, group) => total + group.port_count, 0),
      groups: contractGroups,
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    };
  }

  function nextSubsystemInterfaceContractPortId(group, direction) {
    const ports = Array.isArray(group && group.interface_contracts) ? group.interface_contracts : [];
    let index = ports.length + 1;
    const normalizedDirection = normalizeSubsystemInterfaceDirection(direction);
    const usedIds = new Set(ports.map((port) => port.id));
    let portId = `${group.id}:${normalizedDirection}:${index}`;
    while (usedIds.has(portId)) {
      index += 1;
      portId = `${group.id}:${normalizedDirection}:${index}`;
    }
    return { portId, index };
  }

  function updateSubsystemGroupInterfaceContracts(groupId, updater) {
    subsystemGroups = subsystemGroups.map((group) => {
      if (group.id !== groupId) return group;
      const currentPorts = normalizeSubsystemInterfaceContracts(group.interface_contracts || [], group.id);
      const nextPorts = normalizeSubsystemInterfaceContracts(updater(currentPorts), group.id);
      return { ...group, interface_contracts: nextPorts };
    });
    syncSubsystemNodeAttributes();
    return subsystemGroupById(groupId);
  }

  function renderSubsystemInterfaceContractEditor() {
    const group = selectedSubsystemGroup();
    const ports = group ? normalizeSubsystemInterfaceContracts(group.interface_contracts || [], group.id) : [];
    if (subsystemInterfaceOwner) {
      subsystemInterfaceOwner.textContent = group ? `${group.name} · ${ports.length} port(s)` : "none";
    }
    const disabled = !group;
    if (subsystemInterfaceDirectionSelect) subsystemInterfaceDirectionSelect.disabled = disabled;
    if (subsystemInterfaceLabelInput) subsystemInterfaceLabelInput.disabled = disabled;
    if (subsystemInterfaceSignalInput) subsystemInterfaceSignalInput.disabled = disabled;
    if (subsystemInterfaceValueTypeSelect) subsystemInterfaceValueTypeSelect.disabled = disabled;
    if (subsystemInterfaceEvidenceStatusSelect) subsystemInterfaceEvidenceStatusSelect.disabled = disabled;
    if (addSubsystemInterfacePortBtn) addSubsystemInterfacePortBtn.disabled = disabled;
    if (removeSubsystemInterfacePortBtn) removeSubsystemInterfacePortBtn.disabled = disabled || ports.length === 0;
    if (subsystemInterfaceContractList) {
      subsystemInterfaceContractList.innerHTML = "";
      if (!group) {
        subsystemInterfaceContractList.textContent = "Select a subsystem to define boundary ports.";
      } else if (!ports.length) {
        subsystemInterfaceContractList.textContent = "No subsystem boundary ports yet. Truth effect: none.";
      } else {
        for (const port of ports) {
          const row = document.createElement("div");
          row.className = "workbench-subsystem-interface-row";
          row.setAttribute("data-subsystem-interface-port-id", port.id);
          row.setAttribute("data-evidence-status", port.evidence_status);
          row.setAttribute("data-truth-effect", "none");
          const direction = document.createElement("strong");
          direction.textContent = port.direction;
          const body = document.createElement("span");
          body.textContent = `${port.label} · ${port.signal_id} · ${port.value_type}`;
          const evidence = document.createElement("em");
          evidence.textContent = port.evidence_status;
          row.append(direction, body, evidence);
          subsystemInterfaceContractList.appendChild(row);
        }
      }
    }
    if (subsystemInterfaceStatus) {
      subsystemInterfaceStatus.textContent = group
        ? `Subsystem boundary contract: ${ports.length} port(s). Truth effect: none.`
        : "Select a subsystem before editing boundary ports. Truth effect: none.";
    }
  }

  function addSubsystemInterfaceContractPort() {
    const group = selectedSubsystemGroup();
    if (!group) {
      if (subsystemInterfaceStatus) {
        subsystemInterfaceStatus.textContent = "Select a subsystem before adding boundary ports.";
      }
      return null;
    }
    recordEditableHistory("add_subsystem_interface_contract_port");
    const direction = normalizeSubsystemInterfaceDirection(
      subsystemInterfaceDirectionSelect && subsystemInterfaceDirectionSelect.value,
    );
    const next = nextSubsystemInterfaceContractPortId(group, direction);
    const port = normalizeSubsystemInterfaceContractRecord({
      id: next.portId,
      group_id: group.id,
      direction,
      port_index: next.index,
      label: subsystemInterfaceLabelInput && subsystemInterfaceLabelInput.value,
      signal_id: subsystemInterfaceSignalInput && subsystemInterfaceSignalInput.value,
      value_type: subsystemInterfaceValueTypeSelect && subsystemInterfaceValueTypeSelect.value,
      evidence_status: subsystemInterfaceEvidenceStatusSelect && subsystemInterfaceEvidenceStatusSelect.value,
      source_ref: `ui_draft.subsystem_interface.${group.id}.${direction}.${next.index}`,
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    }, group.id, next.index);
    updateSubsystemGroupInterfaceContracts(group.id, (ports) => [...ports, port]);
    shell.setAttribute("data-draft-state", "derived");
    renderInspector();
    updateEditableDraftHash();
    persistDraft();
    if (draftLabel) draftLabel.textContent = "sandbox_candidate subsystem interface contract pending";
    return port;
  }

  function removeSubsystemInterfaceContractPort() {
    const group = selectedSubsystemGroup();
    if (!group) {
      if (subsystemInterfaceStatus) {
        subsystemInterfaceStatus.textContent = "Select a subsystem before removing boundary ports.";
      }
      return null;
    }
    const ports = normalizeSubsystemInterfaceContracts(group.interface_contracts || [], group.id);
    if (!ports.length) return null;
    recordEditableHistory("remove_subsystem_interface_contract_port");
    const removed = ports[ports.length - 1];
    updateSubsystemGroupInterfaceContracts(group.id, (currentPorts) => currentPorts.slice(0, -1));
    shell.setAttribute("data-draft-state", "derived");
    renderInspector();
    updateEditableDraftHash();
    persistDraft();
    if (draftLabel) draftLabel.textContent = "sandbox_candidate subsystem interface contract pending";
    return removed;
  }

  function nextSubsystemGroupId() {
    while (subsystemGroups.some((group) => group.id === `subsystem_${nextSubsystemGroupIndex}`)) {
      nextSubsystemGroupIndex += 1;
    }
    const groupId = `subsystem_${nextSubsystemGroupIndex}`;
    nextSubsystemGroupIndex += 1;
    return groupId;
  }

  function renderSubsystemOverlays() {
    if (!canvas) return;
    for (const existing of Array.from(canvas.querySelectorAll(".workbench-subsystem-overlay"))) {
      existing.remove();
    }
    const groups = subsystemGroupsSnapshot();
    for (const group of groups) {
      const groupNodes = group.node_ids
        .map((nodeId) => nodes.find((node) => editableNodeId(node) === nodeId))
        .filter(Boolean);
      if (!groupNodes.length) continue;
      const positions = groupNodes.map((node) => editableNodePosition(node));
      const minX = Math.max(2, Math.min(...positions.map((position) => position.x)) - 10);
      const maxX = Math.min(98, Math.max(...positions.map((position) => position.x)) + 10);
      const minY = Math.max(4, Math.min(...positions.map((position) => position.y)) - 9);
      const maxY = Math.min(96, Math.max(...positions.map((position) => position.y)) + 9);
      const overlay = document.createElement("div");
      overlay.className = "workbench-subsystem-overlay";
      overlay.setAttribute("data-subsystem-id", group.id);
      overlay.setAttribute("data-truth-effect", "none");
      overlay.style.setProperty("--subsystem-left", `${minX}%`);
      overlay.style.setProperty("--subsystem-top", `${minY}%`);
      overlay.style.setProperty("--subsystem-width", `${Math.max(8, maxX - minX)}%`);
      overlay.style.setProperty("--subsystem-height", `${Math.max(8, maxY - minY)}%`);
      const label = document.createElement("span");
      label.textContent = group.name;
      overlay.appendChild(label);
      canvas.appendChild(overlay);
    }
  }

  function renderSubsystemEditor() {
    const selectedDraftNodes = selectedEditableDraftNodes();
    const group = selectedSubsystemGroup();
    if (subsystemOwner) {
      subsystemOwner.textContent = group
        ? `${group.name} · ${group.node_ids.length}`
        : `${selectedDraftNodes.length} draft selected`;
    }
    if (subsystemNameInput) {
      subsystemNameInput.value = group ? group.name : normalizeSubsystemGroupName("", subsystemGroups.length + 1);
    }
    if (createSubsystemBtn) createSubsystemBtn.disabled = selectedDraftNodes.length < 2;
    if (renameSubsystemBtn) renameSubsystemBtn.disabled = !group;
    if (ungroupSubsystemBtn) ungroupSubsystemBtn.disabled = !group;
    if (subsystemStatus) {
      subsystemStatus.textContent = group
        ? `Subsystem ${group.id}: ${group.node_ids.length} draft node(s). Truth effect: none.`
        : "Select two or more draft nodes to create a subsystem. Truth effect: none.";
    }
    renderSubsystemInterfaceContractEditor();
  }

  function groupSelectedDraftNodes() {
    const selectedDraftNodes = selectedEditableDraftNodes();
    if (selectedDraftNodes.length < 2) {
      if (subsystemStatus) {
        subsystemStatus.textContent = "Select at least two draft nodes before grouping. Truth effect: none.";
      }
      return null;
    }
    recordEditableHistory("create_subsystem_group");
    const nodeIds = selectedDraftNodes.map((node) => editableNodeId(node)).filter(Boolean);
    const nodeIdSet = new Set(nodeIds);
    subsystemGroups = subsystemGroups
      .map((group) => ({
        ...group,
        node_ids: group.node_ids.filter((nodeId) => !nodeIdSet.has(nodeId)),
      }))
      .filter((group) => group.node_ids.length > 0);
    const groupId = nextSubsystemGroupId();
    const group = normalizeSubsystemGroupRecord({
      id: groupId,
      name: subsystemNameInput && subsystemNameInput.value,
      node_ids: nodeIds,
      source_ref: `ui_draft.subsystem_group.${groupId}`,
      truth_effect: "none",
    }, subsystemGroups.length + 1);
    subsystemGroups.push(group);
    shell.setAttribute("data-draft-state", "derived");
    syncSubsystemNodeAttributes();
    renderEditableEdges();
    renderInspector();
    validateEditableGraph();
    updateEditableDraftHash();
    persistDraft();
    if (draftLabel) draftLabel.textContent = "sandbox_candidate subsystem group pending";
    if (subsystemStatus) {
      subsystemStatus.textContent =
        `Created ${group.name} with ${group.node_ids.length} draft node(s). Truth effect: none.`;
    }
    return group;
  }

  function renameSelectedSubsystemGroup() {
    const group = selectedSubsystemGroup();
    if (!group) {
      if (subsystemStatus) subsystemStatus.textContent = "Select a subsystem before renaming.";
      return null;
    }
    recordEditableHistory("rename_subsystem_group");
    const nextName = normalizeSubsystemGroupName(
      subsystemNameInput && subsystemNameInput.value,
      subsystemGroups.indexOf(group) + 1,
    );
    subsystemGroups = subsystemGroups.map((candidate) => (
      candidate.id === group.id ? { ...candidate, name: nextName } : candidate
    ));
    shell.setAttribute("data-draft-state", "derived");
    syncSubsystemNodeAttributes();
    renderEditableEdges();
    renderInspector();
    updateEditableDraftHash();
    persistDraft();
    if (draftLabel) draftLabel.textContent = "sandbox_candidate subsystem rename pending";
    if (subsystemStatus) {
      subsystemStatus.textContent = `Renamed subsystem ${group.id} to ${nextName}. Truth effect: none.`;
    }
    return subsystemGroupById(group.id);
  }

  function ungroupSelectedSubsystem() {
    const group = selectedSubsystemGroup();
    if (!group) {
      if (subsystemStatus) subsystemStatus.textContent = "Select a subsystem before ungrouping.";
      return null;
    }
    recordEditableHistory("ungroup_subsystem_group");
    const groupNodeIds = new Set(group.node_ids);
    subsystemGroups = subsystemGroups.filter((candidate) => candidate.id !== group.id);
    selectedNodeIds = new Set(Array.from(groupNodeIds).filter((nodeId) => (
      nodes.some((node) => editableNodeId(node) === nodeId)
    )));
    selectedNode = nodes.find((node) => selectedNodeIds.has(editableNodeId(node))) || selectedNode;
    shell.setAttribute("data-draft-state", "derived");
    syncSubsystemNodeAttributes();
    syncEditableNodeSelectionAttributes();
    renderEditableEdges();
    renderInspector();
    validateEditableGraph();
    updateEditableDraftHash();
    persistDraft();
    if (draftLabel) draftLabel.textContent = "sandbox_candidate subsystem ungroup pending";
    if (subsystemStatus) {
      subsystemStatus.textContent = `Ungrouped ${group.name}. Nodes, ports, and edges preserved.`;
    }
    return group;
  }

  function nodeComponentTemplateMetadata(node) {
    const templateId = node && node.getAttribute("data-component-template-id");
    if (!templateId) return null;
    return {
      template_id: templateId,
      template_label: node.getAttribute("data-component-template-label") || templateId,
      template_node_index: Number.parseInt(
        node.getAttribute("data-component-template-node-index") || "0",
        10,
      ),
      library_version: node.getAttribute("data-component-library-version") || componentLibraryVersion,
      source_ref: node.getAttribute("data-component-template-source-ref")
        || `ui_draft.component_library.${templateId}`,
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    };
  }

  function setNodeComponentTemplateMetadata(node, metadata) {
    if (!node || !metadata || typeof metadata !== "object") return;
    const templateId = String(metadata.template_id || metadata.templateId || "").trim();
    if (!templateId) return;
    node.setAttribute("data-component-template-id", templateId);
    node.setAttribute(
      "data-component-template-label",
      String(metadata.template_label || metadata.templateLabel || templateId),
    );
    node.setAttribute(
      "data-component-template-node-index",
      String(metadata.template_node_index || metadata.templateNodeIndex || 0),
    );
    node.setAttribute(
      "data-component-library-version",
      String(metadata.library_version || metadata.libraryVersion || componentLibraryVersion),
    );
    node.setAttribute(
      "data-component-template-source-ref",
      String(metadata.source_ref || metadata.sourceRef || `ui_draft.component_library.${templateId}`),
    );
  }

  function normalizeWorkspaceActionLog(value) {
    if (!Array.isArray(value)) return [];
    return value
      .filter((entry) => entry && typeof entry === "object" && !Array.isArray(entry))
      .map((entry, index) => ({
        index: Number.isFinite(Number(entry.index)) ? Number(entry.index) : index + 1,
        action: String(entry.action || "edit"),
        recorded_at: String(entry.recorded_at || entry.recordedAt || "browser_local_draft"),
        parent_revision_id: entry.parent_revision_id || entry.parentRevisionId || null,
        candidate_state: "sandbox_candidate",
        truth_effect: "none",
      }));
  }

  function normalizeWorkspaceDocumentRecord(record) {
    if (!record || typeof record !== "object" || Array.isArray(record)) return null;
    return {
      document_id: String(record.document_id || record.documentId || workspaceDocumentId),
      revision_id: String(record.revision_id || record.revisionId || workspaceDocumentRevision),
      parent_revision_id: record.parent_revision_id || record.parentRevisionId || null,
      action_log: normalizeWorkspaceActionLog(record.action_log || record.actionLog || []),
    };
  }

  function adoptWorkspaceDocumentRecord(record) {
    const normalized = normalizeWorkspaceDocumentRecord(record);
    if (!normalized) return;
    workspaceDocumentId = normalized.document_id || workspaceDocumentId;
    workspaceDocumentRevision = normalized.revision_id || workspaceDocumentRevision;
    workspaceDocumentParentRevision = normalized.parent_revision_id || null;
    workspaceActionLog = normalized.action_log;
  }

  function workspaceActionLogDigest() {
    return editableDraftHash(stableEvidenceArchiveJson(workspaceActionLog));
  }

  function updateWorkspaceDocumentRevision() {
    const revisionPayload = {
      document_id: workspaceDocumentId,
      draft_state: shell.getAttribute("data-draft-state") || "baseline",
      selected_node_ids: Array.from(selectedNodeIds).sort(),
      viewport_state: viewportStateSnapshot(),
      subsystem_groups: subsystemGroupsSnapshot(),
      captured_subsystem_templates: capturedSubsystemTemplateSnapshot(),
      nodes: nodes.map((node) => editableNodeState(node)),
      edges: draftEdges.map((edge) => ({ ...edge })),
      selected_scenario_id: selectedWorkbenchScenarioId(),
      action_log_digest: workspaceActionLogDigest(),
      undo_depth: undoStack.length,
      redo_depth: redoStack.length,
    };
    const nextRevision = editableDraftHash(stableEvidenceArchiveJson(revisionPayload));
    if (nextRevision !== workspaceDocumentRevision) {
      workspaceDocumentParentRevision =
        workspaceDocumentRevision && workspaceDocumentRevision !== "ui_draft_pending"
          ? workspaceDocumentRevision
          : workspaceDocumentParentRevision;
      workspaceDocumentRevision = nextRevision;
    }
    return workspaceDocumentRevision;
  }

  function currentWorkspaceDocument() {
    const revisionId = updateWorkspaceDocumentRevision();
    return {
      kind: workspaceDocumentKind,
      version: workspaceDocumentVersion,
      document_id: workspaceDocumentId,
      revision_id: revisionId,
      parent_revision_id: workspaceDocumentParentRevision,
      action_count: workspaceActionLog.length,
      action_log_digest: workspaceActionLogDigest(),
      undo_depth: undoStack.length,
      redo_depth: redoStack.length,
      action_log: workspaceActionLog.map((entry) => ({ ...entry })),
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    };
  }

  function renderWorkspaceDocumentStatus(documentRecord) {
    const record = documentRecord || currentWorkspaceDocument();
    if (workspaceDocumentRevisionSlot) {
      workspaceDocumentRevisionSlot.textContent = record.revision_id || "ui_draft_pending";
    }
    if (workspaceDocumentActionCountSlot) {
      workspaceDocumentActionCountSlot.textContent = String(record.action_count || 0);
    }
    if (workspaceDocumentUndoDepthSlot) {
      workspaceDocumentUndoDepthSlot.textContent = String(record.undo_depth || 0);
    }
    if (workspaceDocumentRedoDepthSlot) {
      workspaceDocumentRedoDepthSlot.textContent = String(record.redo_depth || 0);
    }
  }

  function recordWorkspaceAction(actionName) {
    const parentRevision = workspaceDocumentRevision || updateWorkspaceDocumentRevision();
    workspaceActionLog.push({
      index: workspaceActionLog.length + 1,
      action: String(actionName || "edit"),
      recorded_at: "browser_local_draft",
      parent_revision_id: parentRevision && parentRevision !== "ui_draft_pending" ? parentRevision : null,
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    });
    if (workspaceActionLog.length > 100) workspaceActionLog = workspaceActionLog.slice(-100);
    workspaceDocumentParentRevision =
      parentRevision && parentRevision !== "ui_draft_pending" ? parentRevision : workspaceDocumentParentRevision;
  }

  function currentCanvasInteractionSummary() {
    refreshEditableNodes();
    const selectedNodeIdList = Array.from(selectedNodeIds)
      .filter((nodeId) => nodes.some((node) => editableNodeId(node) === nodeId))
      .sort();
    const selectedEdgeId = selectedEdge && selectedEdge.id ? String(selectedEdge.id) : "";
    const positionDigest = editableDraftHash(stableEvidenceArchiveJson(
      nodes.map((node) => ({
        id: editableNodeId(node),
        x: node.style.getPropertyValue("--node-x") || "50%",
        y: node.style.getPropertyValue("--node-y") || "50%",
      })),
    ));
    return {
      kind: canvasInteractionSummaryKind,
      version: canvasInteractionSummaryVersion,
      selected_node_count: selectedNodeIdList.length,
      selected_node_ids: selectedNodeIdList,
      selected_edge_count: selectedEdgeId ? 1 : 0,
      selected_edge_id: selectedEdgeId,
      last_action: lastCanvasInteractionAction || "init",
      node_count: nodes.length,
      draft_node_count: nodes.filter((node) => node.getAttribute("data-draft-node") === "true").length,
      edge_count: draftEdges.length,
      position_digest: positionDigest,
      workspace_action_count: workspaceActionLog.length,
      undo_depth: undoStack.length,
      redo_depth: redoStack.length,
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    };
  }

  function renderCanvasInteractionStatus(summaryRecord) {
    const summary = summaryRecord || currentCanvasInteractionSummary();
    if (canvasSelectedNodeCountSlot) {
      canvasSelectedNodeCountSlot.textContent = String(summary.selected_node_count || 0);
    }
    if (canvasSelectedEdgeCountSlot) {
      canvasSelectedEdgeCountSlot.textContent = String(summary.selected_edge_count || 0);
    }
    if (canvasLastActionSlot) {
      canvasLastActionSlot.textContent = summary.last_action || "init";
    }
  }

  function recordCanvasInteractionAction(actionName) {
    lastCanvasInteractionAction = String(actionName || "edit");
    renderCanvasInteractionStatus();
  }

  function sortedEditableGraphIds(records) {
    if (!Array.isArray(records)) return [];
    return records
      .map((record) => String((record && (record.id || record.port_id || record.group_id)) || ""))
      .filter(Boolean)
      .sort();
  }

  function editableGraphDigest(value) {
    return editableDraftHash(stableEvidenceArchiveJson(value));
  }

  function sortedEditableGraphRecords(records) {
    if (!Array.isArray(records)) return [];
    return records
      .map((record) => normalizeEvidenceArchiveValue(record))
      .sort((left, right) => {
        const leftId = String((left && (left.id || left.port_id || left.group_id)) || "");
        const rightId = String((right && (right.id || right.port_id || right.group_id)) || "");
        return leftId.localeCompare(rightId);
      });
  }

  function buildEditableGraphCanonicalModel(source) {
    const payload = source && typeof source === "object" && !Array.isArray(source)
      ? source
      : {};
    const componentLibrary =
      payload.component_library && typeof payload.component_library === "object" && !Array.isArray(payload.component_library)
        ? payload.component_library
        : {};
    const sandboxTestBench =
      payload.sandbox_test_bench && typeof payload.sandbox_test_bench === "object" && !Array.isArray(payload.sandbox_test_bench)
        ? payload.sandbox_test_bench
        : null;
    const hardwareInterfaceDesigner =
      payload.hardware_interface_designer
      && typeof payload.hardware_interface_designer === "object"
      && !Array.isArray(payload.hardware_interface_designer)
        ? payload.hardware_interface_designer
        : null;
    const workspaceDocument =
      payload.workspace_document && typeof payload.workspace_document === "object" && !Array.isArray(payload.workspace_document)
        ? payload.workspace_document
        : {};
    return {
      schema_version: editableGraphCanonicalModelVersion,
      draft_state: String(payload.draft_state || "derived"),
      canvas_authoring_mode: normalizeCanvasAuthoringMode(payload.canvas_authoring_mode),
      nodes: normalizeEvidenceArchiveValue(Array.isArray(payload.nodes) ? payload.nodes : []),
      edges: normalizeEvidenceArchiveValue(Array.isArray(payload.edges) ? payload.edges : []),
      ports: normalizeEvidenceArchiveValue(Array.isArray(payload.ports) ? payload.ports : []),
      typed_ports: normalizeEvidenceArchiveValue(Array.isArray(payload.typed_ports) ? payload.typed_ports : []),
      subsystem_groups: normalizeEvidenceArchiveValue(Array.isArray(payload.subsystem_groups) ? payload.subsystem_groups : []),
      component_library: normalizeEvidenceArchiveValue(componentLibrary),
      sandbox_test_bench: normalizeEvidenceArchiveValue(sandboxTestBench),
      hardware_bindings: normalizeEvidenceArchiveValue(Array.isArray(payload.hardware_bindings) ? payload.hardware_bindings : []),
      hardware_interface_designer: normalizeEvidenceArchiveValue(hardwareInterfaceDesigner),
      selected_node_ids: normalizeEvidenceArchiveValue(Array.isArray(payload.selected_node_ids) ? payload.selected_node_ids : []),
      viewport_state: normalizeEvidenceArchiveValue(
        payload.viewport_state && typeof payload.viewport_state === "object" && !Array.isArray(payload.viewport_state)
          ? payload.viewport_state
          : {},
      ),
      workspace_document_ref: {
        document_id: String(workspaceDocument.document_id || workspaceDocumentId),
        revision_id: String(workspaceDocument.revision_id || workspaceDocumentRevision),
      },
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    };
  }

  function buildEditableGraphDomAdapterBoundary(source, canonicalModel) {
    const payload = source && typeof source === "object" && !Array.isArray(source)
      ? source
      : {};
    const model = canonicalModel && typeof canonicalModel === "object" && !Array.isArray(canonicalModel)
      ? canonicalModel
      : buildEditableGraphCanonicalModel(payload);
    return {
      kind: "workbench-editable-graph-dom-adapter-boundary",
      version: editableGraphDomAdapterBoundaryVersion,
      source_of_truth: "editable_graph_document.canonical_model",
      renderer: "workbench.html#workbench-editable-canvas",
      node_selector: ".workbench-editable-node",
      edge_selector: ".workbench-editable-edges [data-editable-edge-id]",
      port_selector: ".workbench-port-handle",
      projection_fields: [
        "nodes",
        "edges",
        "ports",
        "typed_ports",
        "subsystem_groups",
        "component_library",
      ],
      top_level_compatibility: true,
      node_count: Array.isArray(model.nodes) ? model.nodes.length : 0,
      edge_count: Array.isArray(model.edges) ? model.edges.length : 0,
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    };
  }

  function buildEditableGraphDocumentFromSnapshot(snapshot) {
    const source = snapshot && typeof snapshot === "object" && !Array.isArray(snapshot)
      ? snapshot
      : {};
    const nodeRecords = Array.isArray(source.nodes) ? source.nodes : [];
    const edgeRecords = Array.isArray(source.edges) ? source.edges : [];
    const portRecords = Array.isArray(source.ports) ? source.ports : [];
    const typedPortRecords = Array.isArray(source.typed_ports) ? source.typed_ports : [];
    const subsystemRecords = Array.isArray(source.subsystem_groups) ? source.subsystem_groups : [];
    const componentLibrary =
      source.component_library && typeof source.component_library === "object" && !Array.isArray(source.component_library)
        ? source.component_library
        : {};
    const capturedTemplates = Array.isArray(componentLibrary.captured_templates)
      ? componentLibrary.captured_templates
      : [];
    const workspaceDocument =
      source.workspace_document && typeof source.workspace_document === "object" && !Array.isArray(source.workspace_document)
        ? source.workspace_document
        : currentWorkspaceDocument();
    const canvasInteractionSummary =
      source.canvas_interaction_summary
      && typeof source.canvas_interaction_summary === "object"
      && !Array.isArray(source.canvas_interaction_summary)
        ? source.canvas_interaction_summary
        : currentCanvasInteractionSummary();
    const nodeIdSet = new Set(sortedEditableGraphIds(nodeRecords));
    const selectedNodeIdList = (Array.isArray(source.selected_node_ids)
      ? source.selected_node_ids
      : Array.from(selectedNodeIds))
      .map((nodeId) => String(nodeId))
      .filter((nodeId) => nodeId && nodeIdSet.has(nodeId))
      .sort();
    const selectedEdgeId = String(
      (canvasInteractionSummary && canvasInteractionSummary.selected_edge_id)
      || (selectedEdge && selectedEdge.id)
      || "",
    );
    const positionRecords = nodeRecords
      .map((node) => ({
        id: String((node && node.id) || ""),
        x: String((node && node.x) || "50%"),
        y: String((node && node.y) || "50%"),
      }))
      .sort((left, right) => left.id.localeCompare(right.id));
    const edgeRouteRecords = edgeRecords
      .map((edge) => ({
        id: String((edge && edge.id) || ""),
        source: String((edge && edge.source) || ""),
        target: String((edge && edge.target) || ""),
        source_port: String((edge && (edge.source_port || edge.sourcePort)) || ""),
        target_port: String((edge && (edge.target_port || edge.targetPort)) || ""),
        edge_label: String((edge && (edge.edge_label || edge.edgeLabel)) || ""),
        route_metadata: edge && (edge.route_metadata || edge.routeMetadata || edge.route)
          ? normalizeEvidenceArchiveValue(edge.route_metadata || edge.routeMetadata || edge.route)
          : null,
      }))
      .sort((left, right) => left.id.localeCompare(right.id));
    const canonicalModel = buildEditableGraphCanonicalModel(source);
    const domAdapter = buildEditableGraphDomAdapterBoundary(source, canonicalModel);
    return {
      kind: editableGraphDocumentKind,
      version: editableGraphDocumentVersion,
      accepted_import_versions: [...editableGraphDocumentAcceptedImportVersions],
      canonical_model: canonicalModel,
      dom_adapter: domAdapter,
      document_id: String(workspaceDocument.document_id || workspaceDocumentId),
      workspace_revision_id: String(workspaceDocument.revision_id || workspaceDocumentRevision),
      workspace_action_count: Number(workspaceDocument.action_count || 0),
      action_log_digest: String(workspaceDocument.action_log_digest || workspaceActionLogDigest()),
      node_count: nodeRecords.length,
      draft_node_count: nodeRecords.filter((node) => Boolean(node && (node.draftNode || node.draft_node))).length,
      edge_count: edgeRecords.length,
      port_count: portRecords.length,
      typed_port_count: typedPortRecords.length,
      subsystem_group_count: subsystemRecords.length,
      component_template_count: capturedTemplates.length,
      selected_node_count: selectedNodeIdList.length,
      selected_edge_count: selectedEdgeId ? 1 : 0,
      node_ids: sortedEditableGraphIds(nodeRecords),
      edge_ids: sortedEditableGraphIds(edgeRecords),
      port_ids: sortedEditableGraphIds(portRecords),
      subsystem_group_ids: sortedEditableGraphIds(subsystemRecords),
      selected_state: {
        node_ids: selectedNodeIdList,
        edge_id: selectedEdgeId,
        truth_effect: "none",
      },
      position_digest: editableGraphDigest(positionRecords),
      node_digest: editableGraphDigest(sortedEditableGraphRecords(nodeRecords)),
      edge_digest: editableGraphDigest(edgeRouteRecords),
      port_digest: editableGraphDigest(sortedEditableGraphRecords(portRecords)),
      subsystem_digest: editableGraphDigest(sortedEditableGraphRecords(subsystemRecords)),
      component_library_digest: editableGraphDigest(componentLibrary),
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    };
  }

  function adoptCanvasInteractionSummary(record) {
    if (!record || typeof record !== "object" || Array.isArray(record)) return;
    if (record.kind === canvasInteractionSummaryKind && typeof record.last_action === "string") {
      lastCanvasInteractionAction = record.last_action || lastCanvasInteractionAction;
    }
  }

  function editableNodeState(node) {
    const componentTemplate = nodeComponentTemplateMetadata(node);
    const subsystemGroup = nodeSubsystemMetadata(node);
    const state = {
      id: node.getAttribute("data-editable-node-id") || "",
      label: node.getAttribute("data-node-label") || "",
      op: node.getAttribute("data-node-op") || "and",
      ruleCount: node.getAttribute("data-rule-count") || "0",
      evidence: node.getAttribute("data-hardware-evidence") || "evidence_gap",
      sourceRef: node.getAttribute("data-source-ref") || "ui_draft",
      op_catalog_entry: node.getAttribute("data-op-catalog-entry")
        || node.getAttribute("data-node-op")
        || "and",
      op_catalog_version: editableOperationCatalogVersion,
      hardware_binding: nodeInterfaceBinding(node),
      x: node.style.getPropertyValue("--node-x") || "50%",
      y: node.style.getPropertyValue("--node-y") || "50%",
      draftNode: node.getAttribute("data-draft-node") === "true",
    };
    if (nodePortContractTouched(node)) {
      state.port_contract = nodePortContract(node);
    }
    if (nodeDraftRulesTouched(node)) {
      state.rules = nodeDraftRules(node);
    }
    if (componentTemplate) {
      state.component_template = componentTemplate;
    }
    if (subsystemGroup) {
      state.subsystem_group = subsystemGroup;
    }
    return state;
  }

  function serializeEditableState() {
    refreshEditableNodes();
    return {
      draftState: shell.getAttribute("data-draft-state") || "baseline",
      canvasAuthoringMode,
      selectedNodeId: selectedNode && selectedNode.getAttribute("data-editable-node-id"),
      selectedNodeIds: Array.from(selectedNodeIds),
      diagnosticFocus: currentDiagnosticFocusSummary(),
      repairActionLog: repairActionLogSnapshot(),
      selectedCatalogOp,
      viewportState: viewportStateSnapshot(),
      workspaceDocument: currentWorkspaceDocument(),
      canvasInteractionSummary: currentCanvasInteractionSummary(),
      sandboxTestBench: safeSandboxTestBenchDefinition(),
      sandboxTestRunReport: currentSandboxTestRunReport(),
      candidateDebuggerView: currentCandidateDebuggerView("storage"),
      preflightAnalyzerReport: currentPreflightAnalyzerReport("storage"),
      hardwareInterfaceDesigner: currentHardwareInterfaceDesignerPayload("storage"),
      hardwareInterfaceDesignerValidation: currentHardwareInterfaceDesignerValidationReport("storage"),
      subsystemGroups: subsystemGroupsSnapshot(),
      capturedSubsystemTemplates: capturedSubsystemTemplateSnapshot(),
      nodes: nodes.map((node) => editableNodeState(node)),
      edges: draftEdges.map((edge) => ({ ...edge })),
    };
  }

  function createEditableNodeElement(nodeState) {
    if (!canvas) return null;
    const node = document.createElement("button");
    node.type = "button";
    node.className = "workbench-editable-node";
    node.setAttribute("data-editable-node-id", nodeState.id);
    node.setAttribute("data-node-label", nodeState.label || nodeState.id);
    node.setAttribute("data-node-op", nodeState.op || "and");
    node.setAttribute("data-rule-count", nodeState.ruleCount || "0");
    node.setAttribute("data-hardware-evidence", nodeState.evidence || "evidence_gap");
    node.setAttribute("data-source-ref", nodeState.sourceRef || "ui_draft.node");
    node.setAttribute(
      "data-op-catalog-entry",
      operationCatalogEntry(nodeState.op_catalog_entry || nodeState.opCatalogEntry || nodeState.op || "and").op,
    );
    node.setAttribute("data-draft-node", nodeState.draftNode ? "true" : "false");
    setNodeInterfaceBinding(node, nodeState.hardware_binding || nodeState.hardwareBinding || {});
    if (nodeState.port_contract || nodeState.portContract) {
      setNodePortContract(node, nodeState.port_contract || nodeState.portContract);
    }
    if (Array.isArray(nodeState.rules)) {
      setNodeDraftRules(node, nodeState.rules);
    }
    setNodeComponentTemplateMetadata(
      node,
      nodeState.component_template || nodeState.componentTemplate || null,
    );
    setNodeSubsystemMetadata(
      node,
      nodeState.subsystem_group || nodeState.subsystemGroup || null,
    );
    node.style.setProperty("--node-x", nodeState.x || "50%");
    node.style.setProperty("--node-y", nodeState.y || "50%");
    node.setAttribute("aria-pressed", "false");
    const label = document.createElement("span");
    label.textContent = nodeState.id;
    const small = document.createElement("small");
    small.textContent = `${(nodeState.op || "and").toUpperCase()} · ${nodeState.ruleCount || "0"} rules`;
    node.append(label, small);
    canvas.appendChild(node);
    attachEditableNodeHandler(node);
    return node;
  }

  function applyEditableState(state) {
    if (!state || typeof state !== "object") return;
    if (typeof state.selectedCatalogOp === "string") {
      setSelectedOperationCatalogEntry(state.selectedCatalogOp);
    }
    canvasAuthoringMode = normalizeCanvasAuthoringMode(
      state.canvasAuthoringMode || state.canvas_authoring_mode || canvasAuthoringMode,
    );
    adoptWorkspaceDocumentRecord(state.workspaceDocument || state.workspace_document || null);
    adoptCanvasInteractionSummary(state.canvasInteractionSummary || state.canvas_interaction_summary || null);
    restoreSandboxTestBenchDefinition(state.sandboxTestBench || state.sandbox_test_bench || null);
    lastSandboxTestRunReport = normalizeImportedSandboxTestRunReport(
      state.sandboxTestRunReport || state.sandbox_test_run_report || lastSandboxTestRunReport,
    );
    if (lastSandboxTestRunReport) {
      renderSandboxTestBenchReport(lastSandboxTestRunReport);
    }
    lastPreflightAnalyzerReport = normalizeImportedPreflightAnalyzerReport(
      state.preflightAnalyzerReport || state.preflight_analyzer_report || lastPreflightAnalyzerReport,
    );
    lastHardwareInterfaceDesignerPayload = normalizeImportedHardwareInterfaceDesignerPayload(
      state.hardwareInterfaceDesigner
        || state.hardware_interface_designer
        || lastHardwareInterfaceDesignerPayload,
    );
    lastHardwareInterfaceDesignerValidationReport = normalizeImportedHardwareInterfaceDesignerValidation(
      state.hardwareInterfaceDesignerValidation
        || state.hardware_interface_designer_validation
        || lastHardwareInterfaceDesignerValidationReport,
    );
    if (lastHardwareInterfaceDesignerPayload && hardwareInterfaceDesignOutput) {
      hardwareInterfaceDesignOutput.value = JSON.stringify(lastHardwareInterfaceDesignerPayload, null, 2);
    }
    if (lastHardwareInterfaceDesignerValidationReport) {
      renderHardwareInterfaceDesignerValidationReport(lastHardwareInterfaceDesignerValidationReport);
    }
    const nodeStates = Array.isArray(state.nodes) ? state.nodes : [];
    subsystemGroups = normalizeSubsystemGroups(
      state.subsystemGroups || state.subsystem_groups || subsystemGroupsFromNodeStates(nodeStates),
    );
    capturedSubsystemTemplates = normalizeCapturedSubsystemTemplates(
      state.capturedSubsystemTemplates
        || state.captured_subsystem_templates
        || state.capturedTemplates
        || state.captured_templates
        || capturedSubsystemTemplates,
    );
    refreshCapturedSubsystemTemplateControls();
    const removableNodeSelector = canvasAuthoringMode === "empty_authoring"
      ? ".workbench-editable-node"
      : '[data-draft-node="true"]';
    for (const existing of Array.from(shell.querySelectorAll(removableNodeSelector))) {
      existing.remove();
    }
    refreshEditableNodes();
    for (const nodeState of nodeStates) {
      if (!nodeState || typeof nodeState !== "object") continue;
      let node = nodes.find((candidate) => (
        candidate.getAttribute("data-editable-node-id") === nodeState.id
      ));
      if (!node) {
        node = createEditableNodeElement(nodeState);
        refreshEditableNodes();
      }
      if (!node) continue;
      if (typeof nodeState.label === "string") node.setAttribute("data-node-label", nodeState.label);
      if (typeof nodeState.op === "string") node.setAttribute("data-node-op", nodeState.op);
      if (typeof nodeState.ruleCount === "string") node.setAttribute("data-rule-count", nodeState.ruleCount);
      if (typeof nodeState.evidence === "string") node.setAttribute("data-hardware-evidence", nodeState.evidence);
      if (typeof nodeState.sourceRef === "string") node.setAttribute("data-source-ref", nodeState.sourceRef);
      node.setAttribute(
        "data-op-catalog-entry",
        operationCatalogEntry(nodeState.op_catalog_entry || nodeState.opCatalogEntry || nodeState.op || "and").op,
      );
      setNodeInterfaceBinding(node, nodeState.hardware_binding || nodeState.hardwareBinding || nodeInterfaceBinding(node));
      if (nodeState.port_contract || nodeState.portContract) {
        setNodePortContract(node, nodeState.port_contract || nodeState.portContract);
      }
      if (Array.isArray(nodeState.rules)) {
        setNodeDraftRules(node, nodeState.rules);
      }
      setNodeComponentTemplateMetadata(
        node,
        nodeState.component_template || nodeState.componentTemplate || null,
      );
      setNodeSubsystemMetadata(
        node,
        nodeState.subsystem_group || nodeState.subsystemGroup || null,
      );
      if (typeof nodeState.x === "string") node.style.setProperty("--node-x", nodeState.x);
      if (typeof nodeState.y === "string") node.style.setProperty("--node-y", nodeState.y);
      updateNodeDisplay(node);
    }
    draftEdges = Array.isArray(state.edges)
      ? state.edges
          .filter((edge) => edge && typeof edge === "object")
          .map((edge, index) => ({
            id: String(edge.id || `edge_imported_${index + 1}`),
            source: String(edge.source || ""),
            target: String(edge.target || ""),
            signal_id: edge.signal_id ? String(edge.signal_id) : undefined,
            source_port_id: edge.source_port_id ? String(edge.source_port_id) : undefined,
            target_port_id: edge.target_port_id ? String(edge.target_port_id) : undefined,
            value_type: edge.value_type ? String(edge.value_type) : undefined,
            unit: edge.unit ? String(edge.unit) : "",
            required: Boolean(edge.required),
            source_ref: edge.source_ref ? String(edge.source_ref) : undefined,
            edge_label: edge.edge_label || edge.edgeLabel ? String(edge.edge_label || edge.edgeLabel) : undefined,
            route_metadata: normalizeEdgeRouteMetadata(edge, edgePortContract(edge)),
            component_template: (
              edge.component_template
              && typeof edge.component_template === "object"
              && !Array.isArray(edge.component_template)
            ) ? edge.component_template : null,
            hardware_binding: normalizeInterfaceBinding(
              edge.hardware_binding || edge.hardwareBinding || {},
              "edge",
              String(edge.id || `edge_imported_${index + 1}`),
            ),
          }))
      : [];
    const selectedId = state.selectedNodeId || (state.selected_node && state.selected_node.id);
    const restoredSelected = nodes.find((node) => (
      node.getAttribute("data-editable-node-id") === selectedId
    ));
    selectedNode = restoredSelected || nodes[0] || null;
    const restoredSelection = Array.isArray(state.selectedNodeIds)
      ? state.selectedNodeIds
          .map((id) => String(id || ""))
          .filter((id) => nodes.some((node) => editableNodeId(node) === id))
      : [];
    const nextViewportState = state.viewportState && typeof state.viewportState === "object"
      ? state.viewportState
      : defaultViewportState();
    selectedDiagnosticFocus =
      state.diagnosticFocus
      && typeof state.diagnosticFocus === "object"
      && state.diagnosticFocus.state === "selected"
        ? normalizeHardwareBindingFocusTarget(state.diagnosticFocus)
        : null;
    repairActionLog = normalizeRepairActionLog(state.repairActionLog || state.repair_action_log || []);
    setViewportState({
      scale: nextViewportState.scale,
      panX: nextViewportState.pan_x !== undefined ? nextViewportState.pan_x : nextViewportState.panX,
      panY: nextViewportState.pan_y !== undefined ? nextViewportState.pan_y : nextViewportState.panY,
    });
    selectedNodeIds = new Set(restoredSelection);
    const activeNodeId = editableNodeId(selectedNode);
    if (activeNodeId && !selectedNodeIds.size) selectedNodeIds.add(activeNodeId);
    syncSubsystemNodeAttributes();
    shell.setAttribute("data-draft-state", state.draftState || "derived");
    syncEditableNodeSelectionAttributes();
    renderEditableEdges();
    renderInspector();
    renderCandidateDebuggerView(currentCandidateDebuggerView("apply_state"));
    renderWorkbenchPreflightAnalyzerReport(currentPreflightAnalyzerReport("apply_state"));
    updateEditableDraftHash();
    validateEditableGraph();
  }

  function recordEditableHistory(_actionName) {
    undoStack.push(serializeEditableState());
    if (undoStack.length > 50) undoStack.shift();
    redoStack.length = 0;
    recordWorkspaceAction(_actionName || "edit");
    recordCanvasInteractionAction(_actionName || "edit");
    renderWorkspaceDocumentStatus();
  }

  function undoEditableEdit() {
    if (!undoStack.length) {
      if (graphValidationStatus) {
        graphValidationStatus.textContent = "Graph validation: no undo step available.";
      }
      return;
    }
    redoStack.push(serializeEditableState());
    applyEditableState(undoStack.pop());
    recordWorkspaceAction("undo_edit");
    renderWorkspaceDocumentStatus();
    persistDraft();
  }

  function redoEditableEdit() {
    if (!redoStack.length) {
      if (graphValidationStatus) {
        graphValidationStatus.textContent = "Graph validation: no redo step available.";
      }
      return;
    }
    undoStack.push(serializeEditableState());
    applyEditableState(redoStack.pop());
    recordWorkspaceAction("redo_edit");
    renderWorkspaceDocumentStatus();
    persistDraft();
  }

  function editableNodePosition(node) {
    const rawX = node && node.style.getPropertyValue("--node-x");
    const rawY = node && node.style.getPropertyValue("--node-y");
    return {
      x: Number.parseFloat(rawX || "50") || 50,
      y: Number.parseFloat(rawY || "50") || 50,
    };
  }

  function edgeTargetPortId(edge) {
    if (!edge || !edge.target) return "";
    const targetNode = nodes.find((node) => node.getAttribute("data-editable-node-id") === edge.target);
    if (targetNode && targetNode.getAttribute("data-draft-node") === "true") {
      return `${edge.target}:in`;
    }
    return `${edge.target}:in:ui_edge:${edge.source || "unknown"}`;
  }

  function edgeInspectorPayload(edge) {
    const sourceNode = nodes.find((node) => node.getAttribute("data-editable-node-id") === edge.source);
    const targetNode = nodes.find((node) => node.getAttribute("data-editable-node-id") === edge.target);
    const missing = [];
    if (!sourceNode) missing.push("source_node");
    if (!targetNode) missing.push("target_node");
    const sourcePortId = edge.source_port_id || edge.sourcePortId || (edge.source ? `${edge.source}:out` : "");
    const targetPortId = edge.target_port_id || edge.targetPortId || edgeTargetPortId(edge);
    const compatibility = portCompatibilityForEdge(edge, collectWorkbenchTypedPorts());
    const contract = edgePortContract(edge);
    const routeMetadata = normalizeEdgeRouteMetadata(edge, contract);
    return {
      id: edge.id || `${edge.source}->${edge.target}`,
      source_node_id: edge.source || "unknown",
      target_node_id: edge.target || "unknown",
      source_port_id: sourcePortId || "evidence_gap",
      target_port_id: targetPortId || "evidence_gap",
      signal_id: edge.signal_id || `${edge.source || "unknown"}__to__${edge.target || "unknown"}`,
      edge_label: edgeWireLabel(edge),
      route_metadata: routeMetadata,
      value_type: normalizePortValueType(edge.value_type || edge.valueType || "boolean"),
      unit: String(edge.unit === null || edge.unit === undefined ? "" : edge.unit).trim(),
      required: normalizePortRequired(edge.required),
      source_port_value_type: compatibility.source_value_type,
      target_port_value_type: compatibility.target_value_type,
      source_port_direction: compatibility.source_direction,
      target_port_direction: compatibility.target_direction,
      port_compatibility_status: compatibility.status,
      evidence_status: missing.length ? "evidence_gap" : "ui_draft",
      validation_issue: missing.length ? `evidence_gap:${missing.join("+")}` : "none",
      truth_effect: "none",
    };
  }

  function edgePathMetadata(edge) {
    const payload = edgeInspectorPayload(edge);
    const binding = edgeInterfaceBinding(edge);
    return [
      `data-source-port-id="${inspectorText(payload.source_port_id)}"`,
      `data-target-port-id="${inspectorText(payload.target_port_id)}"`,
      `data-edge-signal-id="${inspectorText(payload.signal_id)}"`,
      `data-edge-label="${inspectorText(payload.edge_label)}"`,
      `data-route-mode="${inspectorText(payload.route_metadata.routing_mode)}"`,
      `data-edge-evidence-status="${inspectorText(payload.evidence_status)}"`,
      `data-port-compatibility="${inspectorText(payload.port_compatibility_status)}"`,
      `data-binding-quality="${inspectorText(binding.binding_quality)}"`,
    ].join(" ");
  }

  function attachEditableEdgeHandlers() {
    if (!edgeSvg) return;
    const paths = Array.from(edgeSvg.querySelectorAll("[data-editable-edge-id]"));
    for (const path of paths) {
      path.addEventListener("click", () => {
        const edgeIndex = Number.parseInt(path.getAttribute("data-editable-edge-index") || "-1", 10);
        if (edgeIndex >= 0) {
          selectEditableEdgeByIndex(edgeIndex);
        } else {
          selectEditableEdge(path.getAttribute("data-editable-edge-id") || "");
        }
      });
      path.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          const edgeIndex = Number.parseInt(path.getAttribute("data-editable-edge-index") || "-1", 10);
          if (edgeIndex >= 0) {
            selectEditableEdgeByIndex(edgeIndex);
          } else {
            selectEditableEdge(path.getAttribute("data-editable-edge-id") || "");
          }
        }
      });
    }
  }

  function clearPortHandleArmedState() {
    if (!canvas) return;
    for (const handle of Array.from(canvas.querySelectorAll("[data-port-handle-armed]"))) {
      handle.removeAttribute("data-port-handle-armed");
    }
  }

  function handlePortHandleClick(handle) {
    if (!handle) return;
    const ownerId = handle.getAttribute("data-port-handle-owner-id") || "";
    const direction = handle.getAttribute("data-port-handle-direction") || "";
    const node = nodes.find((candidate) => editableNodeId(candidate) === ownerId);
    const payload = portHandlePayload(node, direction);
    if (!payload) return;
    if (direction === "out") {
      pendingPortHandleSource = payload;
      clearPortHandleArmedState();
      handle.setAttribute("data-port-handle-armed", "true");
      if (graphValidationStatus) {
        graphValidationStatus.textContent =
          `Graph validation: output port armed ${payload.port_id}; select an input port. Truth effect: none.`;
      }
      return;
    }
    if (direction !== "in") return;
    if (!pendingPortHandleSource) {
      if (graphValidationStatus) {
        graphValidationStatus.textContent =
          `Graph validation: select an output port before input ${payload.port_id}.`;
      }
      return;
    }
    connectEditableEdge(pendingPortHandleSource.node_id, payload.node_id, {
      source_port_id: pendingPortHandleSource.port_id,
      target_port_id: payload.port_id,
      signal_id: `${pendingPortHandleSource.signal_id}__to__${payload.signal_id}`,
      value_type: pendingPortHandleSource.value_type !== "unknown"
        ? pendingPortHandleSource.value_type
        : payload.value_type,
      unit: pendingPortHandleSource.unit || payload.unit,
      required: Boolean(pendingPortHandleSource.required || payload.required),
      source_ref: "ui_draft.port_handle_wiring",
    });
    pendingPortHandleSource = null;
    clearPortHandleArmedState();
  }

  function attachPortHandleHandlers(handle) {
    handle.addEventListener("pointerdown", (event) => {
      event.preventDefault();
      event.stopPropagation();
    });
    handle.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      handlePortHandleClick(handle);
    });
    handle.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        event.stopPropagation();
        handlePortHandleClick(handle);
      }
    });
  }

  function renderEditablePortHandles() {
    if (!canvas) return;
    for (const existing of Array.from(canvas.querySelectorAll(".workbench-port-handle"))) {
      existing.remove();
    }
    refreshEditableNodes();
    for (const node of nodes) {
      const position = editableNodePosition(node);
      for (const direction of ["in", "out"]) {
        const payload = portHandlePayload(node, direction);
        if (!payload) continue;
        const handle = document.createElement("button");
        handle.type = "button";
        handle.className = "workbench-port-handle";
        handle.setAttribute("data-port-handle-direction", direction);
        handle.setAttribute("data-port-handle-owner-id", payload.node_id);
        handle.setAttribute("data-port-id", payload.port_id);
        handle.setAttribute("data-signal-id", payload.signal_id);
        handle.setAttribute("data-value-type", payload.value_type);
        handle.setAttribute("data-truth-effect", "none");
        handle.setAttribute(
          "aria-label",
          `${direction === "out" ? "Output" : "Input"} port ${payload.port_id}`,
        );
        handle.style.setProperty("--node-x", formatCanvasPercent(position.x));
        handle.style.setProperty("--node-y", formatCanvasPercent(position.y));
        if (
          pendingPortHandleSource
          && direction === "out"
          && pendingPortHandleSource.node_id === payload.node_id
          && pendingPortHandleSource.port_id === payload.port_id
        ) {
          handle.setAttribute("data-port-handle-armed", "true");
        }
        attachPortHandleHandlers(handle);
        canvas.appendChild(handle);
      }
    }
  }

  function renderEditableEdges() {
    if (!edgeSvg) return;
    refreshEditableNodes();
    const paths = [];
    for (let index = 0; index < draftEdges.length; index += 1) {
      const edge = draftEdges[index];
      const sourceNode = nodes.find((node) => node.getAttribute("data-editable-node-id") === edge.source);
      const targetNode = nodes.find((node) => node.getAttribute("data-editable-node-id") === edge.target);
      const source = editableNodePosition(sourceNode);
      const target = editableNodePosition(targetNode);
      const midX = (source.x + target.x) / 2;
      const midY = (source.y + target.y) / 2;
      const payload = edgeInspectorPayload(edge);
      paths.push([
        `<path data-editable-edge-id="${inspectorText(edge.id)}"`,
        `data-editable-edge-index="${index}"`,
        `data-edge-source="${inspectorText(edge.source)}"`,
        `data-edge-target="${inspectorText(edge.target)}"`,
        edgePathMetadata(edge),
        'role="button"',
        'tabindex="0"',
        `aria-label="${inspectorText(`Edge ${edge.source} to ${edge.target}`)}"`,
        `d="M${source.x} ${source.y} C${midX} ${source.y} ${midX} ${target.y} ${target.x} ${target.y}" />`,
        `<text class="workbench-edge-label" data-editable-edge-label-id="${inspectorText(edge.id)}"`,
        `data-edge-label="${inspectorText(payload.edge_label)}"`,
        `data-route-mode="${inspectorText(payload.route_metadata.routing_mode)}"`,
        `x="${midX}" y="${Math.max(4, midY - 1.5)}">`,
        inspectorText(payload.edge_label),
        "</text>",
      ].join(" "));
    }
    edgeSvg.innerHTML = paths.join("");
    const selectedIndex = selectedEdge ? draftEdges.indexOf(selectedEdge) : -1;
    if (selectedIndex >= 0) {
      const path = edgeSvg.querySelector(`[data-editable-edge-index="${selectedIndex}"]`);
      if (path) path.setAttribute("aria-pressed", "true");
    }
    syncEditableNodeSelectionAttributes();
    attachEditableEdgeHandlers();
    renderSubsystemOverlays();
    renderEditablePortHandles();
  }

  function validateEditableGraph() {
    refreshEditableNodes();
    const nodeIds = new Set(nodes.map((node) => node.getAttribute("data-editable-node-id") || ""));
    const seenEdges = new Set();
    const issues = [];
    for (const edge of draftEdges) {
      const edgeKey = `${edge.source}->${edge.target}`;
      if (!edge.source || !edge.target || !nodeIds.has(edge.source) || !nodeIds.has(edge.target)) {
        issues.push(`dangling_port:${edge.id || edgeKey}`);
      }
      if (edge.source && edge.target && edge.source === edge.target) {
        issues.push(`invalid_edge:self_loop:${edge.source}`);
      }
      if (seenEdges.has(edgeKey)) {
        issues.push(`invalid_edge:duplicate:${edgeKey}`);
      }
      seenEdges.add(edgeKey);
    }
    if (graphValidationStatus) {
      let statusText = "Graph validation: no issues.";
      if (issues.length) {
        statusText = `Graph validation: ${issues.join(", ")}`;
      } else if (nodes.length === 0) {
        statusText = "Graph validation: empty sandbox draft. Add a primitive node. Truth effect: none.";
      } else if (selectedNodeIds.size > 1) {
        statusText = `Graph validation: no issues. Multi-select: ${selectedNodeIds.size} nodes.`;
      }
      graphValidationStatus.textContent = statusText;
    }
    return issues;
  }

  function updateEditableDraftHash() {
    const hash = editableDraftHash(stableEvidenceArchiveJson(currentDraftSnapshot()));
    shell.setAttribute("data-draft-hash", hash);
    if (draftHashLabel) draftHashLabel.textContent = hash;
    renderWorkspaceDocumentStatus();
    return hash;
  }

  function setEditorTool(tool) {
    currentEditorTool = tool || "select";
    for (const button of toolbarButtons) {
      button.setAttribute(
        "aria-pressed",
        button.getAttribute("data-editor-tool") === currentEditorTool ? "true" : "false",
      );
    }
  }

  function nextDraftNodeId() {
    refreshEditableNodes();
    while (nodes.some((node) => node.getAttribute("data-editable-node-id") === `draft_node_${nextDraftNodeIndex}`)) {
      nextDraftNodeIndex += 1;
    }
    const nodeId = `draft_node_${nextDraftNodeIndex}`;
    nextDraftNodeIndex += 1;
    return nodeId;
  }

  function startEmptyCanvasDraft() {
    recordEditableHistory("start_empty_canvas_draft");
    canvasAuthoringMode = "empty_authoring";
    shell.setAttribute("data-draft-state", "derived");
    for (const node of Array.from(shell.querySelectorAll(".workbench-editable-node"))) {
      node.remove();
    }
    nodes = [];
    draftEdges = [];
    selectedNode = null;
    selectedNodeIds = new Set();
    selectedEdge = null;
    pendingEdgeSourceId = "";
    pendingPortHandleSource = null;
    selectedDiagnosticFocus = null;
    subsystemGroups = [];
    nextDraftNodeIndex = 1;
    if (draftLabel) {
      draftLabel.textContent = "sandbox_candidate empty graph pending";
    }
    if (componentLibraryStatus) {
      componentLibraryStatus.textContent = "Empty sandbox canvas ready";
    }
    setTimelineState("derived");
    syncEditableNodeSelectionAttributes();
    renderEditableEdges();
    renderInspector();
    validateEditableGraph();
    updateEditableDraftHash();
    persistDraft();
  }

  function addEditableNode() {
    recordEditableHistory("add_node");
    canvasAuthoringMode = normalizeCanvasAuthoringMode(canvasAuthoringMode);
    shell.setAttribute("data-draft-state", "derived");
    const nodeId = nextDraftNodeId();
    const catalogEntry = operationCatalogEntry(selectedCatalogOp);
    const node = createEditableNodeElement({
      id: nodeId,
      label: `Draft ${catalogEntry.label}`,
      op: catalogEntry.op,
      ruleCount: catalogEntry.rule_count,
      evidence: "evidence_gap",
      sourceRef: `ui_draft.op_catalog.${catalogEntry.op}.${nodeId}`,
      op_catalog_entry: catalogEntry.op,
      port_contract: portContractForCatalogNode(nodeId, catalogEntry),
      x: `${42 + (nextDraftNodeIndex % 5) * 8}%`,
      y: `${24 + (nextDraftNodeIndex % 4) * 10}%`,
      draftNode: true,
    });
    refreshEditableNodes();
    if (node) selectNode(node);
    if (draftLabel) draftLabel.textContent = "sandbox_candidate node edit pending";
    setTimelineState("derived");
    renderEditableEdges();
    validateEditableGraph();
    updateEditableDraftHash();
    persistDraft();
  }

  function componentTemplateNodeState(template, nodeTemplate, index, baseX, baseY, idMap) {
    const nodeId = nodeTemplate.__new_node_id || nextDraftNodeId();
    const catalogEntry = operationCatalogEntry(nodeTemplate.op || "and");
    const remappedBinding = remapTemplateValue(nodeTemplate.hardware_binding || nodeTemplate.hardwareBinding || {}, idMap || {});
    const remappedPortContract = remapTemplateValue(
      nodeTemplate.port_contract || nodeTemplate.portContract || portContractForCatalogNode(nodeId, catalogEntry),
      idMap || {},
    );
    const remappedRules = remapTemplateValue(nodeTemplate.rules || [], idMap || {});
    return {
      id: nodeId,
      label: nodeTemplate.label || template.label || catalogEntry.label,
      op: catalogEntry.op,
      ruleCount: String(nodeTemplate.rule_count || catalogEntry.rule_count || "0"),
      evidence: String(nodeTemplate.evidence || "evidence_gap"),
      sourceRef: `ui_draft.component_library.${template.id}.node.${index + 1}`,
      op_catalog_entry: catalogEntry.op,
      hardware_binding: normalizeInterfaceBinding(remappedBinding, "node", nodeId),
      port_contract: {
        ...normalizePortContract(remappedPortContract, nodeId),
        source_ref: `ui_draft.component_library.${template.id}.port_contract.${index + 1}`,
      },
      rules: Array.isArray(remappedRules) ? remappedRules : [],
      component_template: {
        template_id: template.id,
        template_label: template.label,
        template_node_index: index,
        library_version: componentLibraryVersion,
        source_ref: `ui_draft.component_library.${template.id}`,
        candidate_state: "sandbox_candidate",
        truth_effect: "none",
      },
      x: `${Math.max(8, Math.min(92, baseX + (nodeTemplate.x_offset || 0)))}%`,
      y: `${Math.max(10, Math.min(90, baseY + (nodeTemplate.y_offset || 0)))}%`,
      draftNode: true,
    };
  }

  function instantiateComponentTemplate(templateId) {
    const template = componentTemplateById(templateId);
    if (!template) {
      if (componentLibraryStatus) {
        componentLibraryStatus.textContent = "Unknown template";
      }
      return [];
    }
    recordEditableHistory(`component_template_${template.id}`);
    shell.setAttribute("data-draft-state", "derived");
    lastComponentTemplateId = template.id;
    const baseX = 34 + (nextDraftNodeIndex % 5) * 8;
    const baseY = 26 + (nextDraftNodeIndex % 4) * 10;
    const preparedNodeTemplates = (template.nodes || []).map((nodeTemplate) => ({
      ...nodeTemplate,
      __new_node_id: nextDraftNodeId(),
    }));
    const idMap = {};
    for (const nodeTemplate of preparedNodeTemplates) {
      const sourceId = String(nodeTemplate.original_node_id || nodeTemplate.originalNodeId || "").trim();
      if (sourceId) idMap[sourceId] = nodeTemplate.__new_node_id;
    }
    const createdNodes = preparedNodeTemplates
      .map((nodeTemplate, index) => (
        createEditableNodeElement(componentTemplateNodeState(template, nodeTemplate, index, baseX, baseY, idMap))
      ))
      .filter(Boolean);
    refreshEditableNodes();
    for (const edgeTemplate of template.edges || []) {
      const sourceNode = createdNodes[edgeTemplate.source_index];
      const targetNode = createdNodes[edgeTemplate.target_index];
      const sourceId = editableNodeId(sourceNode);
      const targetId = editableNodeId(targetNode);
      if (!sourceId || !targetId) continue;
      const edgeId = `edge_component_${template.id}_${sourceId}_${targetId}`;
      const remappedBinding = remapTemplateValue(edgeTemplate.hardware_binding || edgeTemplate.hardwareBinding || {}, idMap);
      draftEdges.push({
        id: edgeId,
        source: sourceId,
        target: targetId,
        source_port_id: remapTemplateValue(edgeTemplate.source_port_id || edgeTemplate.sourcePortId || `${sourceId}:out`, idMap),
        target_port_id: remapTemplateValue(edgeTemplate.target_port_id || edgeTemplate.targetPortId || `${targetId}:in`, idMap),
        signal_id: remapTemplateValue(edgeTemplate.signal_id || edgeTemplate.signalId || `${sourceId}__to__${targetId}`, idMap),
        value_type: normalizePortValueType(edgeTemplate.value_type || "boolean"),
        unit: String(edgeTemplate.unit || ""),
        required: normalizePortRequired(edgeTemplate.required),
        source_ref: `ui_draft.component_library.${template.id}.edge`,
        component_template: {
          template_id: template.id,
          library_version: componentLibraryVersion,
          source_ref: `ui_draft.component_library.${template.id}`,
          candidate_state: "sandbox_candidate",
          truth_effect: "none",
        },
        hardware_binding: normalizeInterfaceBinding(remappedBinding, "edge", edgeId),
      });
    }
    if (template.subsystem || template.subsystem_group || template.subsystemGroup) {
      const templateSubsystem = template.subsystem || template.subsystem_group || template.subsystemGroup || {};
      const groupId = nextSubsystemGroupId();
      const remappedInterfaceContracts = normalizeSubsystemInterfaceContracts(
        (templateSubsystem.interface_contracts || templateSubsystem.interfaceContracts || []).map((port, index) => ({
          ...remapTemplateValue(port, idMap),
          id: `${groupId}:${normalizeSubsystemInterfaceDirection(port.direction)}:${index + 1}`,
          group_id: groupId,
          port_index: index + 1,
          source_ref: `ui_draft.component_library.${template.id}.subsystem_interface.${index + 1}`,
          candidate_state: "sandbox_candidate",
          truth_effect: "none",
        })),
        groupId,
      );
      subsystemGroups.push(normalizeSubsystemGroupRecord({
        id: groupId,
        name: `${normalizeCapturedTemplateLabel(template.label, subsystemGroups.length + 1)} copy`,
        node_ids: createdNodes.map((node) => editableNodeId(node)).filter(Boolean),
        interface_contracts: remappedInterfaceContracts,
        source_ref: `ui_draft.component_library.${template.id}.subsystem`,
        truth_effect: "none",
      }, subsystemGroups.length + 1));
    }
    refreshEditableNodes();
    selectedNode = createdNodes[createdNodes.length - 1] || selectedNode;
    selectedNodeIds = new Set(createdNodes.map((node) => editableNodeId(node)).filter(Boolean));
    syncEditableNodeSelectionAttributes();
    renderInspector();
    if (draftLabel) draftLabel.textContent = "sandbox_candidate component template pending";
    if (componentLibraryStatus) {
      componentLibraryStatus.textContent = `${template.short_label} · inserted`;
    }
    setTimelineState("derived");
    renderEditableEdges();
    validateEditableGraph();
    updateEditableDraftHash();
    persistDraft();
    return createdNodes;
  }

  function selectedNodesForSubsystemTemplateCapture() {
    refreshEditableNodes();
    const group = selectedSubsystemGroup();
    if (group && group.node_ids.length) {
      return group.node_ids
        .map((nodeId) => nodes.find((node) => editableNodeId(node) === nodeId))
        .filter((node) => node && node.getAttribute("data-draft-node") === "true");
    }
    return selectedEditableDraftNodes();
  }

  function captureSelectedSubsystemTemplate() {
    const group = selectedSubsystemGroup();
    const sourceNodes = selectedNodesForSubsystemTemplateCapture();
    if (!group && sourceNodes.length < 2) {
      if (componentLibraryStatus) {
        componentLibraryStatus.textContent = "Select a subsystem or at least two draft nodes before capture.";
      }
      return null;
    }
    if (!sourceNodes.length) {
      if (componentLibraryStatus) {
        componentLibraryStatus.textContent = "No draft nodes available for capture.";
      }
      return null;
    }
    recordEditableHistory("capture_subsystem_template");
    const templateId = nextCapturedSubsystemTemplateId();
    const sourceNodeIds = sourceNodes.map((node) => editableNodeId(node)).filter(Boolean);
    const sourceNodeIdSet = new Set(sourceNodeIds);
    const positions = sourceNodes.map((node) => editableNodePosition(node));
    const centerX = positions.reduce((total, position) => total + position.x, 0) / positions.length;
    const centerY = positions.reduce((total, position) => total + position.y, 0) / positions.length;
    const templateNodes = sourceNodes.map((node, index) => {
      const state = editableNodeState(node);
      const position = positions[index];
      return normalizeCapturedTemplateNodeRecord({
        original_node_id: state.id,
        label: state.label,
        op: state.op,
        rule_count: state.ruleCount,
        evidence: state.evidence,
        source_ref: state.sourceRef,
        op_catalog_entry: state.op_catalog_entry,
        hardware_binding: state.hardware_binding,
        port_contract: state.port_contract || portContractForCatalogNode(state.id, operationCatalogEntry(state.op)),
        rules: state.rules || [],
        x_offset: Number((position.x - centerX).toFixed(2)),
        y_offset: Number((position.y - centerY).toFixed(2)),
        candidate_state: "sandbox_candidate",
        truth_effect: "none",
      }, index + 1);
    }).filter(Boolean);
    const templateEdges = draftEdges
      .filter((edge) => sourceNodeIdSet.has(edge.source) && sourceNodeIdSet.has(edge.target))
      .map((edge, index) => normalizeCapturedTemplateEdgeRecord({
        original_edge_id: edge.id,
        source_index: sourceNodeIds.indexOf(edge.source),
        target_index: sourceNodeIds.indexOf(edge.target),
        source_port_id: edge.source_port_id || `${edge.source}:out`,
        target_port_id: edge.target_port_id || `${edge.target}:in`,
        signal_id: edge.signal_id || `${edge.source}__to__${edge.target}`,
        value_type: edge.value_type || "boolean",
        unit: edge.unit || "",
        required: edge.required,
        source_ref: edge.source_ref || `ui_draft.component_library.${templateId}.edge.${index + 1}`,
        hardware_binding: edgeInterfaceBinding(edge),
        candidate_state: "sandbox_candidate",
        truth_effect: "none",
      }, index + 1))
      .filter(Boolean);
    const sourceSubsystem = normalizeSubsystemGroupRecord({
      id: group ? group.id : `captured_subsystem_${templateId}`,
      name: group ? group.name : normalizeCapturedTemplateLabel(
        subsystemNameInput && subsystemNameInput.value,
        capturedSubsystemTemplates.length + 1,
      ),
      node_ids: sourceNodeIds,
      interface_contracts: group ? group.interface_contracts || [] : [],
      source_ref: group ? group.source_ref : `ui_draft.component_library.${templateId}.subsystem`,
      truth_effect: "none",
    }, capturedSubsystemTemplates.length + 1);
    const template = normalizeCapturedSubsystemTemplateRecord({
      id: templateId,
      label: sourceSubsystem ? sourceSubsystem.name : `Captured subsystem ${capturedSubsystemTemplates.length + 1}`,
      short_label: "CAP",
      capture_source: group
        ? `ui_draft.subsystem_group.${group.id}`
        : "ui_draft.component_library.multi_select",
      subsystem: sourceSubsystem,
      nodes: templateNodes,
      edges: templateEdges,
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_effect: "none",
    }, capturedSubsystemTemplates.length + 1);
    if (!template) return null;
    capturedSubsystemTemplates = normalizeCapturedSubsystemTemplates([...capturedSubsystemTemplates, template]);
    lastComponentTemplateId = template.id;
    shell.setAttribute("data-draft-state", "derived");
    refreshCapturedSubsystemTemplateControls();
    renderInspector();
    updateEditableDraftHash();
    persistDraft();
    if (draftLabel) draftLabel.textContent = "sandbox_candidate captured subsystem template pending";
    if (componentLibraryStatus) {
      componentLibraryStatus.textContent =
        `${template.short_label} · captured ${template.nodes.length} node(s). Truth effect: none.`;
    }
    return template;
  }

  function insertLatestCapturedSubsystemTemplate() {
    const latest = capturedSubsystemTemplates[capturedSubsystemTemplates.length - 1];
    if (!latest) {
      if (componentLibraryStatus) {
        componentLibraryStatus.textContent = "No captured subsystem template available.";
      }
      refreshCapturedSubsystemTemplateControls();
      return [];
    }
    return instantiateComponentTemplate(latest.id);
  }

  function duplicateEditableNodeFromSource(sourceNode, offsetIndex) {
    const source = editableNodeState(sourceNode);
    const sourcePosition = editableNodePosition(sourceNode);
    const nodeId = nextDraftNodeId();
    const offset = 6 * (offsetIndex || 1);
    const copiedBinding = {
      hardware_id: source.hardware_binding && source.hardware_binding.hardware_id,
      cable: source.hardware_binding && source.hardware_binding.cable,
      connector: source.hardware_binding && source.hardware_binding.connector,
      port_local: source.hardware_binding && String(source.hardware_binding.port_local || "").replace(source.id, nodeId),
      port_peer: source.hardware_binding && String(source.hardware_binding.port_peer || "").replace(source.id, nodeId),
      evidence_status: source.hardware_binding && source.hardware_binding.evidence_status,
    };
    const copiedPortContract = source.port_contract ? {
      ...source.port_contract,
      input_port_id: `${nodeId}:in`,
      output_port_id: `${nodeId}:out`,
      input_signal_id: `${nodeId}_${source.op || "and"}_input`,
      output_signal_id: `${nodeId}_${source.op || "and"}_output`,
      source_ref: `ui_draft.duplicate.${source.id}.port_contract`,
    } : null;
    const copiedRules = Array.isArray(source.rules)
      ? source.rules.map((rule, index) => ({
          ...rule,
          name: `${rule.name || "draft_rule"}_${nodeId}_${index + 1}`,
        }))
      : [];
    return createEditableNodeElement({
      id: nodeId,
      label: `${source.label || source.id} copy`,
      op: source.op || "and",
      ruleCount: source.ruleCount || "0",
      evidence: source.evidence || "evidence_gap",
      sourceRef: `ui_draft.duplicate.${source.id}.${nodeId}`,
      op_catalog_entry: source.op_catalog_entry || source.op || "and",
      hardware_binding: copiedBinding,
      port_contract: copiedPortContract,
      rules: copiedRules,
      x: `${Math.min(92, sourcePosition.x + offset)}%`,
      y: `${Math.min(92, sourcePosition.y + offset)}%`,
      draftNode: true,
    });
  }

  function duplicateSelectedEditableNode() {
    const sourceNodes = selectedEditableDraftNodes();
    if (!sourceNodes.length) {
      if (graphValidationStatus) {
        graphValidationStatus.textContent =
          selectedNode
            ? "Graph validation: Baseline reference nodes cannot be duplicated."
            : "Graph validation: select a draft node before duplicating.";
      }
      return null;
    }
    recordEditableHistory(sourceNodes.length > 1 ? "batch_duplicate_nodes" : "duplicate_node");
    shell.setAttribute("data-draft-state", "derived");
    const createdNodes = sourceNodes
      .map((sourceNode, index) => duplicateEditableNodeFromSource(sourceNode, index + 1))
      .filter(Boolean);
    refreshEditableNodes();
    selectedNode = createdNodes[createdNodes.length - 1] || selectedNode;
    selectedNodeIds = new Set(createdNodes.map((node) => editableNodeId(node)).filter(Boolean));
    syncEditableNodeSelectionAttributes();
    renderInspector();
    if (draftLabel) draftLabel.textContent = "sandbox_candidate duplicate node edit pending";
    setTimelineState("derived");
    renderEditableEdges();
    validateEditableGraph();
    updateEditableDraftHash();
    persistDraft();
    if (graphValidationStatus && createdNodes.length > 1) {
      graphValidationStatus.textContent =
        `Graph validation: batch duplicated ${createdNodes.length} draft nodes.`;
    }
    return createdNodes[createdNodes.length - 1] || null;
  }

  function removeSelectedEditableNode() {
    const draftNodesToRemove = selectedEditableDraftNodes();
    if (!draftNodesToRemove.length) {
      if (graphValidationStatus) {
        graphValidationStatus.textContent =
          selectedNode
            ? "Graph validation: Baseline reference nodes cannot be removed."
            : "Graph validation: select a draft node before removing.";
      }
      return;
    }
    recordEditableHistory(draftNodesToRemove.length > 1 ? "batch_remove_nodes" : "remove_node");
    const removedNodeIds = new Set(draftNodesToRemove.map((node) => editableNodeId(node)));
    selectedDiagnosticFocus = null;
    for (const node of draftNodesToRemove) {
      node.remove();
    }
    draftEdges = draftEdges.filter((edge) => !removedNodeIds.has(edge.source) && !removedNodeIds.has(edge.target));
    refreshEditableNodes();
    syncSubsystemNodeAttributes();
    selectedNode = nodes[0] || null;
    selectedNodeIds = new Set(selectedNode ? [editableNodeId(selectedNode)] : []);
    syncEditableNodeSelectionAttributes();
    if (draftLabel) draftLabel.textContent = "sandbox_candidate node edit pending";
    renderEditableEdges();
    renderInspector();
    validateEditableGraph();
    updateEditableDraftHash();
    persistDraft();
  }

  function beginEditableGroupDrag(event, node) {
    if (!event || event.button !== 0 || !node) return;
    if (spacePanActive || currentEditorTool !== "select" || isSelectionModifier(event)) return;
    if (node.getAttribute("data-draft-node") !== "true") return;
    if (groupDragState && pointerEventMatchesState(event, groupDragState)) return;
    if (!selectedNodeIds.has(editableNodeId(node))) {
      setSingleEditableNodeSelection(node);
      renderInspector();
    }
    const draftNodesToMove = selectedEditableDraftNodes();
    if (!draftNodesToMove.length) return;
    groupDragState = {
      pointerId: event.pointerId,
      start: canvasPointPercent(event),
      moved: false,
      historyRecorded: false,
      nodes: draftNodesToMove.map((candidate) => ({
        node: candidate,
        id: editableNodeId(candidate),
        position: editableNodePosition(candidate),
      })),
    };
    if (typeof node.setPointerCapture === "function") {
      try {
        node.setPointerCapture(event.pointerId);
      } catch (err) {
        // Synthetic browser events can report a stale pointer capture target;
        // window/canvas fallbacks below still carry the active drag state.
      }
    }
  }

  function beginEditableGroupDragFromEventTarget(event) {
    if (!event || groupDragState) return;
    const target = event.target;
    if (!(target instanceof Element)) return;
    const node = target.closest(".workbench-editable-node");
    if (!node) return;
    beginEditableGroupDrag(event, node);
  }

  function applyEditableGroupDragPosition(event) {
    if (!groupDragState || !pointerEventMatchesState(event, groupDragState)) return;
    const current = canvasPointPercent(event);
    const dx = current.x - groupDragState.start.x;
    const dy = current.y - groupDragState.start.y;
    if (!groupDragState.moved && Math.abs(dx) + Math.abs(dy) < 0.8) return;
    event.preventDefault();
    if (!groupDragState.historyRecorded) {
      recordEditableHistory(groupDragState.nodes.length > 1 ? "group_move_nodes" : "move_node");
      groupDragState.historyRecorded = true;
    }
    groupDragState.moved = true;
    shell.setAttribute("data-draft-state", "derived");
    for (const item of groupDragState.nodes) {
      setEditableNodePosition(
        item.node,
        item.position.x + dx,
        item.position.y + dy,
      );
    }
    renderEditableEdges();
    updateEditableDraftHash();
    if (graphValidationStatus) {
      graphValidationStatus.textContent =
        `Graph validation: moving ${groupDragState.nodes.length} draft node(s). Truth effect: none.`;
    }
    return true;
  }

  function updateEditableGroupDrag(event) {
    applyEditableGroupDragPosition(event);
  }

  function endEditableGroupDrag(event) {
    if (!groupDragState || !pointerEventMatchesState(event, groupDragState)) return;
    applyEditableGroupDragPosition(event);
    const movedCount = groupDragState.nodes.length;
    const didMove = groupDragState.moved;
    const movedNodes = groupDragState.nodes.map((item) => item.node).filter(Boolean);
    const movedNodeIds = groupDragState.nodes.map((item) => item.id).filter(Boolean);
    groupDragState = null;
    if (!didMove) return;
    selectedNode = movedNodes[movedNodes.length - 1] || selectedNode;
    selectedNodeIds = new Set(movedNodeIds);
    syncEditableNodeSelectionAttributes();
    suppressNextNodeClick = true;
    if (draftLabel) draftLabel.textContent = "sandbox_candidate group move pending";
    validateEditableGraph();
    updateEditableDraftHash();
    persistDraft();
    if (graphValidationStatus) {
      graphValidationStatus.textContent =
        `Graph validation: group moved ${movedCount} draft node(s). Truth effect: none.`;
    }
    window.setTimeout(() => { suppressNextNodeClick = false; }, 0);
  }

  function beginCanvasLasso(event) {
    if (!canvas || !event || currentEditorTool !== "select") return;
    if (beginViewportPan(event)) return;
    if (event.button !== 0) return;
    const target = event.target;
    if (
      target instanceof Element
      && (
        target.closest(".workbench-editable-node")
        || target.closest("[data-editable-edge-id]")
        || target.closest("input, textarea, select, button")
      )
    ) {
      return;
    }
    const start = canvasPointPercent(event);
    lassoDragState = {
      pointerId: event.pointerId,
      start,
      additive: isSelectionModifier(event),
      active: false,
    };
    canvas.setPointerCapture(event.pointerId);
  }

  function updateCanvasLasso(event) {
    if (updateViewportPan(event)) return;
    if (!lassoDragState || !pointerEventMatchesState(event, lassoDragState)) return;
    const current = canvasPointPercent(event);
    const rect = lassoRectFromPoints(lassoDragState.start, current);
    if (!lassoDragState.active && rect.width + rect.height < 1.2) return;
    event.preventDefault();
    lassoDragState.active = true;
    setSelectionMarqueeRect(rect);
  }

  function endCanvasLasso(event) {
    if (endViewportPan(event)) return;
    if (!lassoDragState || !pointerEventMatchesState(event, lassoDragState)) return;
    const current = canvasPointPercent(event);
    const rect = lassoRectFromPoints(lassoDragState.start, current);
    const shouldApply = lassoDragState.active && (rect.width + rect.height >= 1.2);
    const additive = lassoDragState.additive;
    lassoDragState = null;
    hideSelectionMarquee();
    if (!shouldApply) return;
    applyLassoSelection(lassoNodesWithinRect(rect), additive);
  }

  function connectEditableEdge(sourceId, targetId, options) {
    if (!sourceId || !targetId || sourceId === targetId) {
      if (graphValidationStatus) {
        graphValidationStatus.textContent = "Graph validation: invalid_edge cannot connect node to itself.";
      }
      return;
    }
    const edgeKey = `${sourceId}->${targetId}`;
    if (draftEdges.some((edge) => `${edge.source}->${edge.target}` === edgeKey)) {
      if (graphValidationStatus) {
        graphValidationStatus.textContent = `Graph validation: invalid_edge duplicate ${edgeKey}.`;
      }
      return;
    }
    recordEditableHistory("connect_edge");
    const newEdgeId = `edge_${sourceId}_${targetId}_${draftEdges.length + 1}`;
    const metadata = options && typeof options === "object" ? options : {};
    const newEdge = {
      id: newEdgeId,
      source: sourceId,
      target: targetId,
      source_port_id: normalizedInterfaceField(metadata.source_port_id || `${sourceId}:out`),
      target_port_id: normalizedInterfaceField(
        metadata.target_port_id || edgeTargetPortId({ source: sourceId, target: targetId }),
      ),
      signal_id: normalizedInterfaceField(metadata.signal_id || `${sourceId}__to__${targetId}`),
      value_type: normalizePortValueType(metadata.value_type || "boolean"),
      unit: String(metadata.unit === null || metadata.unit === undefined ? "" : metadata.unit).trim(),
      required: normalizePortRequired(metadata.required),
      source_ref: normalizedInterfaceField(metadata.source_ref || "ui_draft.edge_tool"),
      hardware_binding: normalizeInterfaceBinding({}, "edge", newEdgeId),
    };
    newEdge.edge_label = edgeWireLabel(newEdge);
    newEdge.route_metadata = normalizeEdgeRouteMetadata(newEdge, edgePortContract(newEdge));
    draftEdges.push(newEdge);
    if (draftLabel) draftLabel.textContent = "sandbox_candidate edge edit pending";
    renderEditableEdges();
    validateEditableGraph();
    updateEditableDraftHash();
    persistDraft();
    if (graphValidationStatus && metadata.source_ref === "ui_draft.port_handle_wiring") {
      graphValidationStatus.textContent =
        `Graph validation: port handle edge ${sourceId}->${targetId} created. Truth effect: none.`;
    }
  }

  function beginEditableEdgeConnect() {
    pendingEdgeSourceId = selectedNode && selectedNode.getAttribute("data-editable-node-id") || "";
    if (graphValidationStatus) {
      graphValidationStatus.textContent = pendingEdgeSourceId
        ? `Graph validation: select target node for edge from ${pendingEdgeSourceId}.`
        : "Graph validation: select a source node before connecting.";
    }
  }

  function disconnectSelectedEditableEdge() {
    if (!draftEdges.length) return;
    if (selectedEdge) {
      const selectedIndex = draftEdges.indexOf(selectedEdge);
      if (selectedIndex >= 0) {
        recordEditableHistory("disconnect_selected_edge");
        draftEdges.splice(selectedIndex, 1);
        selectedEdge = null;
        selectedDiagnosticFocus = null;
        if (draftLabel) draftLabel.textContent = "sandbox_candidate edge edit pending";
        renderEditableEdges();
        renderInspector();
        validateEditableGraph();
        updateEditableDraftHash();
        persistDraft();
        return;
      }
    }
    const selectedId = selectedNode && selectedNode.getAttribute("data-editable-node-id");
    const index = selectedId
      ? draftEdges.findIndex((edge) => edge.source === selectedId || edge.target === selectedId)
      : draftEdges.length - 1;
    const removeIndex = index >= 0 ? index : draftEdges.length - 1;
    recordEditableHistory("disconnect_edge");
    draftEdges.splice(removeIndex, 1);
    selectedDiagnosticFocus = null;
    if (draftLabel) draftLabel.textContent = "sandbox_candidate edge edit pending";
    renderEditableEdges();
    validateEditableGraph();
    updateEditableDraftHash();
    persistDraft();
  }

  function persistDraft() {
    try {
      window.localStorage.setItem(storageKey, JSON.stringify(serializeEditableState()));
    } catch (_err) {
      // Draft persistence is a convenience. Failure must not block the workbench.
    }
  }

  function normalizeDraftSnapshotName(value, fallbackIndex) {
    const text = String(value === null || value === undefined ? "" : value).trim();
    return text || `candidate-${fallbackIndex || 1}`;
  }

  function normalizeDraftSnapshotRecord(record, fallbackIndex) {
    if (!record || typeof record !== "object" || Array.isArray(record)) return null;
    const draft = record.draft && typeof record.draft === "object" ? record.draft : null;
    if (!draft || !Array.isArray(draft.nodes)) return null;
    const name = normalizeDraftSnapshotName(record.name, fallbackIndex);
    const hash = String(
      record.draft_hash || editableDraftHash(stableEvidenceArchiveJson({
        draft,
        selected_scenario_id: record.selected_scenario_id || "nominal_landing",
        custom_snapshot: record.custom_snapshot || {},
      })),
    );
    return {
      kind: "well-harness-workbench-draft-snapshot",
      version: 1,
      id: String(record.id || `${hash}_${fallbackIndex || 1}`),
      name,
      saved_at: String(record.saved_at || "browser_local_draft"),
      draft_hash: hash,
      draft_state: String(record.draft_state || draft.draftState || "derived"),
      selected_scenario_id: String(record.selected_scenario_id || "nominal_landing"),
      custom_snapshot: (
        record.custom_snapshot
        && typeof record.custom_snapshot === "object"
        && !Array.isArray(record.custom_snapshot)
      ) ? record.custom_snapshot : {},
      draft,
      truth_level_impact: "none",
      dal_pssa_impact: "none",
      controller_truth_modified: false,
      truth_effect: "none",
    };
  }

  function readNamedDraftSnapshots() {
    try {
      const raw = window.localStorage.getItem(snapshotsStorageKey);
      const payload = raw ? JSON.parse(raw) : [];
      if (!Array.isArray(payload)) return [];
      return payload
        .map((record, index) => normalizeDraftSnapshotRecord(record, index + 1))
        .filter(Boolean);
    } catch (_err) {
      return [];
    }
  }

  function writeNamedDraftSnapshots(records) {
    const normalized = (Array.isArray(records) ? records : [])
      .map((record, index) => normalizeDraftSnapshotRecord(record, index + 1))
      .filter(Boolean);
    try {
      window.localStorage.setItem(snapshotsStorageKey, JSON.stringify(normalized));
    } catch (_err) {
      // Snapshot persistence is convenience-only local evidence.
    }
    return normalized;
  }

  function selectedDraftSnapshotId() {
    return draftSnapshotSelect ? String(draftSnapshotSelect.value || "") : "";
  }

  function buildDraftSnapshotManifestSummary(records) {
    const snapshots = Array.isArray(records) ? records : readNamedDraftSnapshots();
    return {
      storage_key: snapshotsStorageKey,
      snapshot_count: snapshots.length,
      active_snapshot_id: selectedDraftSnapshotId() || null,
      snapshots: snapshots.map((record) => ({
        id: record.id,
        name: record.name,
        saved_at: record.saved_at,
        draft_hash: record.draft_hash,
        draft_state: record.draft_state,
        selected_scenario_id: record.selected_scenario_id,
      })),
      truth_level_impact: "none",
      truth_effect: "none",
    };
  }

  function renderDraftSnapshotManager(selectedId) {
    if (!draftSnapshotSelect) return buildDraftSnapshotManifestSummary();
    const records = readNamedDraftSnapshots();
    const activeId = selectedId || selectedDraftSnapshotId();
    if (!records.length) {
      draftSnapshotSelect.innerHTML = '<option value="">No saved snapshots</option>';
    } else {
      draftSnapshotSelect.innerHTML = records.map((record) => [
        `<option value="${inspectorText(record.id)}"`,
        record.id === activeId ? 'selected="selected"' : "",
        ">",
        `${inspectorText(record.name)} · ${inspectorText(record.draft_hash)}`,
        "</option>",
      ].join(" ")).join("");
    }
    if (draftSnapshotStatus) {
      draftSnapshotStatus.textContent =
        `Draft snapshots: ${records.length} local sandbox candidate(s). Truth effect: none.`;
    }
    return buildDraftSnapshotManifestSummary(records);
  }

  function saveNamedDraftSnapshot() {
    const existing = readNamedDraftSnapshots();
    const name = normalizeDraftSnapshotName(
      draftSnapshotNameInput && draftSnapshotNameInput.value,
      existing.length + 1,
    );
    const draft = serializeEditableState();
    const customSnapshot = safeWorkbenchCustomSnapshot() || {};
    const hash = editableDraftHash(stableEvidenceArchiveJson({
      draft,
      selected_scenario_id: selectedWorkbenchScenarioId(),
      custom_snapshot: customSnapshot,
    }));
    const record = normalizeDraftSnapshotRecord({
      id: `${hash}_${Date.now().toString(36)}`,
      name,
      saved_at: new Date().toISOString(),
      draft_hash: hash,
      draft_state: draft.draftState || "derived",
      selected_scenario_id: selectedWorkbenchScenarioId(),
      custom_snapshot: customSnapshot,
      draft,
    }, existing.length + 1);
    const saved = writeNamedDraftSnapshots([...existing, record]);
    renderDraftSnapshotManager(record.id);
    if (draftSnapshotNameInput) draftSnapshotNameInput.value = name;
    if (draftSnapshotStatus) {
      draftSnapshotStatus.textContent =
        `Saved ${name} (${hash}). Local sandbox evidence only; truth effect: none.`;
    }
    return saved;
  }

  function restoreNamedDraftSnapshot() {
    const snapshotId = selectedDraftSnapshotId();
    const record = readNamedDraftSnapshots().find((item) => item.id === snapshotId);
    if (!record) {
      if (draftSnapshotStatus) draftSnapshotStatus.textContent = "No draft snapshot selected.";
      return null;
    }
    recordEditableHistory("restore_named_snapshot");
    if (scenarioSelect) scenarioSelect.value = record.selected_scenario_id || "nominal_landing";
    if (customSnapshotInput) customSnapshotInput.value = JSON.stringify(record.custom_snapshot || {}, null, 2);
    applyEditableState({
      ...record.draft,
      draftState: record.draft_state || "derived",
    });
    if (draftLabel) {
      draftLabel.textContent = `sandbox_candidate restored from snapshot: ${record.name}`;
    }
    setTimelineState("derived");
    persistDraft();
    renderDraftSnapshotManager(record.id);
    if (draftSnapshotStatus) {
      draftSnapshotStatus.textContent =
        `Restored ${record.name} (${record.draft_hash}). Truth effect: none.`;
    }
    return record;
  }

  function deleteNamedDraftSnapshot() {
    const snapshotId = selectedDraftSnapshotId();
    if (!snapshotId) {
      if (draftSnapshotStatus) draftSnapshotStatus.textContent = "No draft snapshot selected.";
      return [];
    }
    const remaining = writeNamedDraftSnapshots(
      readNamedDraftSnapshots().filter((record) => record.id !== snapshotId),
    );
    renderDraftSnapshotManager(remaining[0] && remaining[0].id);
    if (draftSnapshotStatus) {
      draftSnapshotStatus.textContent =
        `Deleted local draft snapshot. Remaining: ${remaining.length}. Truth effect: none.`;
    }
    return remaining;
  }

  function selectedDebugTimelineVerdictValue() {
    if (lastSandboxDiff && lastSandboxDiff.verdict) return lastSandboxDiff.verdict;
    const rendered = diffVerdict && String(diffVerdict.textContent || "").trim();
    return rendered || "not_run";
  }

  function selectedDebugTimelineState(verdict) {
    if (verdict === "running") return "running";
    if (["equivalent", "divergent", "invalid_model", "invalid_scenario"].includes(verdict)) {
      return "linked_to_latest_diff";
    }
    return "selection_only";
  }

  function selectedDebugTimelineContextForTarget(target, binding) {
    const selectedBinding = binding || (target && target.binding) || {};
    if (!target || target.kind === "none") {
      return {
        target_kind: "none",
        target_id: "none",
        context_label: "No selected graph element.",
        graph: {},
        binding: normalizeInterfaceBinding(selectedBinding, "none", "none"),
      };
    }
    if (target.kind === "edge" && selectedEdge) {
      const payload = edgeInspectorPayload(selectedEdge);
      return {
        target_kind: "edge",
        target_id: target.id,
        context_label: `${payload.source_node_id} -> ${payload.target_node_id} / ${payload.signal_id}`,
        graph: {
          source_node_id: payload.source_node_id,
          target_node_id: payload.target_node_id,
          source_port_id: payload.source_port_id,
          target_port_id: payload.target_port_id,
          signal_id: payload.signal_id,
          port_compatibility_status: payload.port_compatibility_status,
          validation_issue: payload.validation_issue,
          truth_effect: "none",
        },
        binding: normalizeInterfaceBinding(selectedBinding, "edge", target.id),
      };
    }
    const payload = selectedNodePayload() || {};
    return {
      target_kind: "node",
      target_id: payload.id || target.id || "unknown",
      context_label: `${payload.op || "and"} / ${payload.ruleCount || "0"} rule(s) / ${payload.sourceRef || "unknown"}`,
      graph: {
        op: payload.op || "and",
        rule_count: payload.ruleCount || "0",
        source_ref: payload.sourceRef || "unknown",
        hardware_evidence: payload.evidence || "evidence_gap",
        truth_effect: "none",
      },
      binding: normalizeInterfaceBinding(selectedBinding, "node", payload.id || target.id || "unknown"),
    };
  }

  function currentSelectedDebugTimelinePacket(state) {
    const target = activeInterfaceBindingTarget();
    const context = selectedDebugTimelineContextForTarget(target, target.binding);
    const verdict = selectedDebugTimelineVerdictValue();
    const binding = context.binding || normalizeInterfaceBinding({}, context.target_kind, context.target_id);
    const gapFields = hardwareEvidenceV2GapFields(binding);
    const latestDiff = lastSandboxDiff || null;
    return {
      kind: "well-harness-workbench-selected-debug-timeline",
      version: 1,
      target_kind: context.target_kind,
      target_id: context.target_id,
      owner_key: `${context.target_kind}:${context.target_id}`,
      candidate_state: "sandbox_candidate",
      workflow_state: state || "selection",
      scenario_id: selectedWorkbenchScenarioId(),
      scenario_metadata: currentWorkbenchScenarioMetadata(),
      diff_verdict: verdict,
      trace_link_status: selectedDebugTimelineState(verdict),
      graph_context: context.graph,
      context_label: context.context_label,
      hardware_binding: binding,
      hardware_overlay: {
        hardware_id: binding.hardware_id,
        connector: binding.connector,
        cable: binding.cable,
        port_local: binding.port_local,
        port_peer: binding.port_peer,
        evidence_status: binding.evidence_status,
        evidence_gap_fields: gapFields,
        truth_effect: "none",
      },
      latest_diff: latestDiff
        ? {
            verdict: latestDiff.verdict || "unknown",
            scenario_id: latestDiff.scenario_id || selectedWorkbenchScenarioId(),
            first_divergence: (
              latestDiff.summary
              && latestDiff.summary.first_divergence
            ) || null,
            truth_level_impact: "none",
          }
        : null,
      truth_effect: "none",
    };
  }

  function renderSelectedDebugTimeline(state) {
    const packet = currentSelectedDebugTimelinePacket(state);
    if (timelineStrip) {
      timelineStrip.setAttribute("data-selected-target", packet.owner_key);
      timelineStrip.setAttribute("data-debug-verdict", packet.diff_verdict);
      timelineStrip.setAttribute("data-debug-state", packet.trace_link_status);
      timelineStrip.setAttribute("data-debug-truth-effect", "none");
    }
    if (selectedDebugTimelineTarget) selectedDebugTimelineTarget.textContent = packet.owner_key;
    if (selectedDebugTimelineScenario) selectedDebugTimelineScenario.textContent = packet.scenario_id;
    if (selectedDebugTimelineVerdict) selectedDebugTimelineVerdict.textContent = packet.diff_verdict;
    if (selectedDebugTimelineLinkStatus) {
      selectedDebugTimelineLinkStatus.textContent = packet.trace_link_status;
    }
    if (selectedDebugTimelineHardware) {
      const overlay = packet.hardware_overlay || {};
      selectedDebugTimelineHardware.textContent =
        `${overlay.hardware_id || "evidence_gap"} / ${overlay.connector || "evidence_gap"} / gaps=${(overlay.evidence_gap_fields || []).length}`;
    }
    if (selectedDebugTimelineContext) {
      selectedDebugTimelineContext.textContent =
        `${packet.context_label} · ${packet.trace_link_status} · truth_effect: none`;
    }
    return packet;
  }

  function normalizeDiffReviewV2Verdict(verdict) {
    const normalized = String(verdict || "not_run").trim();
    if (["equivalent", "divergent", "invalid_model", "invalid_scenario"].includes(normalized)) {
      return normalized;
    }
    return "not_run";
  }

  function diffReviewV2ReadinessState(verdict) {
    if (verdict === "equivalent") return "ready";
    if (verdict === "divergent") return "review_required";
    if (verdict === "invalid_model" || verdict === "invalid_scenario") return "blocked";
    return "run_required";
  }

  function diffReviewV2ArchiveStateValue(verdict) {
    return verdict === "not_run" ? "not_archive_ready" : "archive_ready";
  }

  function diffReviewV2FirstDivergenceText(diffPayload) {
    if (!diffPayload) return "not run";
    const verdict = normalizeDiffReviewV2Verdict(diffPayload.verdict);
    if (verdict === "invalid_model" || verdict === "invalid_scenario") {
      const validationText = graphValidationReportText(diffPayload.validation_report);
      return [
        diffPayload.error || verdict,
        validationText,
      ].filter(Boolean).join(" | ");
    }
    return firstDivergenceText(diffPayload.summary && diffPayload.summary.first_divergence);
  }

  function currentCandidateBaselineDiffReviewV2Report(state, modelHash, sourceDiff) {
    const diffPayload = sourceDiff || lastSandboxDiff || null;
    const verdict = normalizeDiffReviewV2Verdict(diffPayload && diffPayload.verdict);
    const selectedTimeline = currentSelectedDebugTimelinePacket("diff_review");
    const hardwareEvidence = currentHardwareEvidenceV2Report();
    const summary = (diffPayload && diffPayload.summary) || {};
    const firstDivergence =
      (summary && summary.first_divergence) || null;
    return {
      kind: "well-harness-workbench-candidate-baseline-diff-review-v2",
      version: 1,
      candidate_state: "sandbox_candidate",
      workflow_state: state || "review",
      verdict,
      allowed_verdicts: ["equivalent", "divergent", "invalid_model", "invalid_scenario"],
      review_readiness: diffReviewV2ReadinessState(verdict),
      archive_state: diffReviewV2ArchiveStateValue(verdict),
      scenario_id: (diffPayload && diffPayload.scenario_id) || selectedWorkbenchScenarioId(),
      scenario_metadata:
        (diffPayload && diffPayload.scenario_metadata) || currentWorkbenchScenarioMetadata(),
      model_hash: modelHash || (diffPayload && diffPayload.model_hash) || "pending",
      selected_target: selectedTimeline.owner_key || "none:none",
      selected_debug_trace_link: selectedTimeline.trace_link_status || "selection_only",
      first_divergence: firstDivergence,
      first_divergence_text: diffReviewV2FirstDivergenceText(diffPayload),
      assertion_status: summary.assertion_status || "not_run",
      frame_count: summary.frame_count || 0,
      validation_status:
        (diffPayload && diffPayload.validation_report && diffPayload.validation_report.status) || "not_run",
      baseline_source: {
        adapter: "reference-deploy-controller",
        truth_level: "certified",
        source: "certified adapter/controller baseline",
      },
      candidate_certification_claim: "none",
      certification_claim: "none",
      truth_level_impact: "none",
      dal_pssa_impact: "none",
      controller_truth_modified: false,
      frozen_assets_modified: false,
      hardware_truth_effect: "none",
      hardware_evidence: {
        target: `${hardwareEvidence.target_kind || "none"}:${hardwareEvidence.target_id || "none"}`,
        coverage_status: hardwareEvidence.coverage_status || "missing",
        evidence_gap_count: hardwareEvidence.evidence_gap_count || 0,
        truth_effect: "none",
      },
      review_guardrails: [
        "Candidate output is sandbox evidence only.",
        "Equivalent does not certify the candidate.",
        "Divergent requires human review before any ChangeRequest.",
        "Invalid model/scenario must be fixed before implementation.",
      ],
      truth_effect: "none",
    };
  }

  function renderCandidateBaselineDiffReviewV2(state, modelHash, sourceDiff) {
    const report = currentCandidateBaselineDiffReviewV2Report(state, modelHash, sourceDiff);
    if (diffReviewV2Panel) {
      diffReviewV2Panel.setAttribute("data-review-verdict", report.verdict);
      diffReviewV2Panel.setAttribute("data-review-readiness", report.review_readiness);
      diffReviewV2Panel.setAttribute("data-review-truth-effect", "none");
    }
    if (diffReviewV2Status) diffReviewV2Status.textContent = report.verdict;
    if (diffReviewV2Target) diffReviewV2Target.textContent = report.selected_target;
    if (diffReviewV2Scenario) diffReviewV2Scenario.textContent = report.scenario_id;
    if (diffReviewV2Readiness) diffReviewV2Readiness.textContent = report.review_readiness;
    if (diffReviewV2ArchiveState) diffReviewV2ArchiveState.textContent = report.archive_state;
    if (diffReviewV2Divergence) diffReviewV2Divergence.textContent = report.first_divergence_text;
    if (diffReviewV2Claim) diffReviewV2Claim.textContent = report.certification_claim;
    return report;
  }

  function setTimelineState(state) {
    if (!timelineStrip) return;
    const items = Array.from(timelineStrip.querySelectorAll("li"));
    for (const item of items) {
      item.setAttribute("data-step-state", "idle");
    }
    if (state === "derived") {
      items[0] && items[0].setAttribute("data-step-state", "done");
      items[1] && items[1].setAttribute("data-step-state", "active");
    } else if (state === "running") {
      items[0] && items[0].setAttribute("data-step-state", "done");
      items[1] && items[1].setAttribute("data-step-state", "done");
      items[2] && items[2].setAttribute("data-step-state", "active");
    } else if (state === "diff") {
      items[0] && items[0].setAttribute("data-step-state", "done");
      items[1] && items[1].setAttribute("data-step-state", "done");
      items[2] && items[2].setAttribute("data-step-state", "done");
      items[3] && items[3].setAttribute("data-step-state", "active");
    } else if (state === "handoff") {
      items[0] && items[0].setAttribute("data-step-state", "done");
      items[1] && items[1].setAttribute("data-step-state", "done");
      items[2] && items[2].setAttribute("data-step-state", "done");
      items[3] && items[3].setAttribute("data-step-state", "done");
      items[4] && items[4].setAttribute("data-step-state", "active");
    }
    renderSelectedDebugTimeline(state);
    renderCandidateBaselineDiffReviewV2(state);
  }

  function normalizeInspectorLogicNodeId(nodeId) {
    const raw = String(nodeId || "").trim();
    const match = raw.match(/^logic([1-4])$/i);
    if (match) return `L${match[1]}`;
    return raw.toUpperCase();
  }

  function evidenceValueText(valueRef) {
    if (!valueRef || typeof valueRef !== "object") {
      return "not recorded (evidence_gap)";
    }
    const status = valueRef.status || "evidence_gap";
    const value = valueRef.value;
    if (status === "evidence_gap" || value === "TBD" || value === null || value === undefined) {
      return "not recorded (evidence_gap)";
    }
    return `${value} (${status})`;
  }

  function inspectorText(value) {
    return String(value === null || value === undefined ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function evidenceRowsForNode(report, nodeId) {
    if (!report || !report.evidence_index || !report.evidence_index.logic_node_bindings) {
      return [];
    }
    const key = normalizeInspectorLogicNodeId(nodeId);
    const rows = report.evidence_index.logic_node_bindings[key];
    return Array.isArray(rows) ? rows : [];
  }

  function renderInspectorEvidenceDetails(payload) {
    const rows = evidenceRowsForNode(hardwareEvidenceReport, payload && payload.id);
    if (signalCountSlot) signalCountSlot.textContent = String(rows.length);
    if (!evidenceDetail) return;
    if (!hardwareEvidenceReport) {
      evidenceDetail.textContent = "Hardware evidence loading. Truth effect remains none.";
      return;
    }
    if (!rows.length) {
      evidenceDetail.innerHTML = [
        '<p class="workbench-inspector-empty">No hardware signal binding is recorded for this node.</p>',
        '<p class="workbench-inspector-truth-note">truth_effect: none</p>',
      ].join("");
      return;
    }
    const items = rows.map((row) => {
      const carrier = [
        `Cable: ${evidenceValueText(row.cable)}`,
        `Connector: ${evidenceValueText(row.connector)}`,
        `Local port: ${evidenceValueText(row.port_local)}`,
        `Peer port: ${evidenceValueText(row.port_peer)}`,
      ].join(" · ");
      const status = row.display_status === "not_recorded" ? "not recorded" : "recorded";
      return [
        '<li>',
        `<strong>${inspectorText(row.signal_id || "unknown_signal")}</strong>`,
        `<span>${inspectorText(row.source_hardware_id || "unknown")} → ${inspectorText(row.peer_hardware_id || "unknown")}</span>`,
        `<small>${inspectorText(carrier)}</small>`,
        `<em>${inspectorText(status)} · truth_effect: ${inspectorText(row.truth_effect || "none")}</em>`,
        '</li>',
      ].join("");
    }).join("");
    evidenceDetail.innerHTML = `<ul>${items}</ul>`;
  }

  function hardwareEvidenceV2GapFields(binding) {
    const base = hardwareBindingEvidenceGapFields(binding);
    for (const fieldName of ["pin_local", "pin_peer"]) {
      if (isInterfaceEvidenceGap(binding && binding[fieldName])) {
        base.push(fieldName);
      }
    }
    return Array.from(new Set(base));
  }

  function hardwareEvidenceV2ReferenceGapCount(rows) {
    return (Array.isArray(rows) ? rows : []).reduce((total, row) => (
      total + ["cable", "connector", "port_local", "port_peer"]
        .filter((fieldName) => evidenceValueRaw(row && row[fieldName]) === "evidence_gap").length
    ), 0);
  }

  function hardwareEvidenceV2FieldRows(binding) {
    const source = binding && typeof binding === "object" ? binding : {};
    return [
      ["hardware_id", "LRU / hardware"],
      ["cable", "Cable"],
      ["connector", "Connector"],
      ["port_local", "Local port"],
      ["port_peer", "Peer port"],
      ["pin_local", "Local pin"],
      ["pin_peer", "Peer pin"],
      ["evidence_status", "Evidence status"],
      ["source_ref", "Source ref"],
    ].map(([key, label]) => {
      const value = normalizedInterfaceField(source[key]);
      return {
        field: key,
        label,
        value,
        status: isInterfaceEvidenceGap(value) ? "evidence_gap" : "recorded",
        truth_effect: "none",
      };
    });
  }

  function buildHardwareEvidenceV2Report(target, referenceRows) {
    const sourceTarget = target && typeof target === "object"
      ? target
      : activeInterfaceBindingTarget();
    const ownerKind = sourceTarget.kind || "none";
    const ownerId = sourceTarget.id || "none";
    const binding = normalizeInterfaceBinding(sourceTarget.binding || {}, ownerKind, ownerId);
    const fieldRows = hardwareEvidenceV2FieldRows(binding);
    const evidenceGapFields = hardwareEvidenceV2GapFields(binding);
    const connectorPinMap = meaningfulInterfaceBinding(binding)
      ? buildWorkbenchConnectorPinMap([binding])
      : buildWorkbenchConnectorPinMap([]);
    const quality = interfaceBindingQualityReport(binding);
    const rows = Array.isArray(referenceRows) ? referenceRows : [];
    return {
      kind: "well-harness-workbench-hardware-evidence-inspector-v2",
      version: 1,
      target_kind: ownerKind,
      target_id: ownerId,
      owner_key: `${ownerKind}:${ownerId}`,
      candidate_state: "sandbox_candidate",
      coverage_status: quality.status,
      coverage_label: quality.label,
      selected_binding: binding,
      fields: fieldRows,
      evidence_gap_count: evidenceGapFields.length,
      evidence_gap_fields: evidenceGapFields,
      connector_pin_row_count: connectorPinMap.row_count || 0,
      connector_pin_evidence_gap_field_count: connectorPinMap.evidence_gap_field_count || 0,
      reference_signal_count: rows.length,
      reference_evidence_gap_count: hardwareEvidenceV2ReferenceGapCount(rows),
      reference_signals: rows.map((row) => ({
        signal_id: normalizedInterfaceField(row && row.signal_id),
        source_hardware_id: normalizedInterfaceField(row && row.source_hardware_id),
        peer_hardware_id: normalizedInterfaceField(row && row.peer_hardware_id),
        carrier_status: normalizedInterfaceField(row && row.carrier_status),
        truth_effect: "none",
      })),
      truth_effect: "none",
    };
  }

  function currentHardwareEvidenceV2Report() {
    const target = activeInterfaceBindingTarget();
    const rows = target.kind === "node"
      ? evidenceRowsForNode(hardwareEvidenceReport, target.id)
      : [];
    return buildHardwareEvidenceV2Report(target, rows);
  }

  function renderHardwareEvidenceV2Report(report) {
    const payload = report || currentHardwareEvidenceV2Report();
    if (hardwareEvidenceV2Status) {
      hardwareEvidenceV2Status.textContent = payload.coverage_status || "missing";
    }
    if (hardwareEvidenceV2Target) {
      hardwareEvidenceV2Target.textContent = `${payload.target_kind}:${payload.target_id}`;
    }
    if (hardwareEvidenceV2Coverage) {
      hardwareEvidenceV2Coverage.textContent =
        `${payload.coverage_label || payload.coverage_status} · truth_effect: none`;
    }
    if (hardwareEvidenceV2GapCount) {
      hardwareEvidenceV2GapCount.textContent =
        `${payload.evidence_gap_count || 0} selected / ${payload.reference_evidence_gap_count || 0} reference`;
    }
    if (hardwareEvidenceV2PinRows) {
      hardwareEvidenceV2PinRows.textContent =
        `${payload.connector_pin_row_count || 0} row(s) / ${payload.connector_pin_evidence_gap_field_count || 0} pin-map gap(s)`;
    }
    if (!hardwareEvidenceV2Fields) return payload;
    const fieldRows = Array.isArray(payload.fields) ? payload.fields : [];
    if (!fieldRows.length) {
      hardwareEvidenceV2Fields.textContent =
        "No selected hardware/interface evidence. Truth effect: none.";
      return payload;
    }
    hardwareEvidenceV2Fields.innerHTML = fieldRows.map((field) => [
      '<div',
      'class="workbench-hardware-evidence-v2-row"',
      `data-gap-state="${field.status === "evidence_gap" ? "gap" : "recorded"}"`,
      `data-evidence-field="${inspectorText(field.field)}"`,
      '>',
      `<strong>${inspectorText(field.label)}</strong>`,
      `<span>${inspectorText(field.value)}</span>`,
      `<em>${inspectorText(field.status)} · truth_effect: none</em>`,
      '</div>',
    ].join(" ")).join("");
    return payload;
  }

  function evidenceValueRaw(valueRef) {
    if (!valueRef || typeof valueRef !== "object") return "evidence_gap";
    const status = String(valueRef.status || "evidence_gap");
    const value = valueRef.value;
    if (status === "evidence_gap" || value === "TBD" || value === null || value === undefined) {
      return "evidence_gap";
    }
    return String(value);
  }

  function hardwarePaletteItemStatus(row) {
    if (!row || typeof row !== "object") return "evidence_gap";
    return String(row.carrier_status || row.value_status || row.display_status || row.evidence_status || "evidence_gap");
  }

  function hardwarePaletteBinding(item, ownerKind, ownerId) {
    const source = item && item.binding && typeof item.binding === "object" ? item.binding : {};
    return normalizeInterfaceBinding({
      hardware_id: source.hardware_id,
      cable: source.cable,
      connector: source.connector,
      port_local: source.port_local,
      port_peer: source.port_peer,
      evidence_status: source.evidence_status,
      source_ref: source.source_ref || (item && item.source_ref),
    }, ownerKind, ownerId);
  }

  function hardwarePalettePortContract(item, nodeId) {
    const signalId = item && item.signal_id ? String(item.signal_id) : "";
    const suffix = item && item.kind ? String(item.kind) : "interface";
    return normalizePortContract({
      input_signal_id: signalId || `${nodeId}_${suffix}_input`,
      output_signal_id: signalId ? `${signalId}_candidate` : `${nodeId}_${suffix}_output`,
      value_type: item && item.value_type ? item.value_type : "unknown",
      unit: "",
      required: false,
      source_ref: `ui_draft.hardware_palette.${item && item.kind ? item.kind : "unknown"}`,
      truth_effect: "none",
    }, nodeId);
  }

  function hardwarePaletteItemsFromEvidence(report) {
    const index = report && report.evidence_index ? report.evidence_index : {};
    const lrus = Array.isArray(index.lru_inventory) ? index.lru_inventory : [];
    const signalBindings = Array.isArray(index.signal_bindings) ? index.signal_bindings : [];
    const items = [];
    for (const lru of lrus) {
      const lruId = normalizedInterfaceField(lru.id);
      items.push({
        id: `lru:${lruId}`,
        kind: "lru",
        label: lru.display_name || lruId,
        detail: lruId,
        status: hardwarePaletteItemStatus(lru),
        source_ref: lru.source_ref || "hardware_evidence.lru_inventory",
        binding: {
          hardware_id: lruId,
          cable: "evidence_gap",
          connector: "evidence_gap",
          port_local: "evidence_gap",
          port_peer: "evidence_gap",
          evidence_status: "evidence_gap",
          source_ref: lru.source_ref || "hardware_evidence.lru_inventory",
        },
        value_type: "unknown",
      });
    }
    for (const row of signalBindings) {
      const signalId = normalizedInterfaceField(row.signal_id);
      const sourceHardwareId = normalizedInterfaceField(row.source_hardware_id);
      const peerHardwareId = normalizedInterfaceField(row.peer_hardware_id);
      const cable = evidenceValueRaw(row.cable);
      const connector = evidenceValueRaw(row.connector);
      const portLocal = evidenceValueRaw(row.port_local);
      const portPeer = evidenceValueRaw(row.port_peer);
      const evidenceStatus = hardwarePaletteItemStatus(row) === "recorded" ? "ui_draft" : "evidence_gap";
      const binding = {
        hardware_id: sourceHardwareId,
        cable,
        connector,
        port_local: portLocal,
        port_peer: portPeer,
        evidence_status: evidenceStatus,
        source_ref: row.source_ref || "hardware_evidence.signal_bindings",
      };
      items.push({
        id: `signal:${signalId}:${sourceHardwareId}:${peerHardwareId}`,
        kind: "signal",
        label: signalId,
        detail: `${sourceHardwareId} -> ${peerHardwareId}`,
        status: hardwarePaletteItemStatus(row),
        source_ref: row.source_ref || "hardware_evidence.signal_bindings",
        signal_id: signalId,
        binding,
        value_type: "unknown",
      });
      items.push({
        id: `carrier:${signalId}:${sourceHardwareId}:${peerHardwareId}`,
        kind: "carrier",
        label: `${signalId} carrier`,
        detail: `Cable ${cable} | Connector ${connector} | Ports ${portLocal} -> ${portPeer}`,
        status: hardwarePaletteItemStatus(row),
        source_ref: row.source_ref || "hardware_evidence.signal_bindings",
        signal_id: signalId,
        binding,
        value_type: "unknown",
      });
    }
    return items;
  }

  function currentHardwarePaletteFilter() {
    return hardwarePaletteFilter ? String(hardwarePaletteFilter.value || "all") : "all";
  }

  function renderHardwarePalette() {
    if (!hardwarePaletteList) return [];
    hardwarePaletteItems = hardwarePaletteItemsFromEvidence(hardwareEvidenceReport);
    const filter = currentHardwarePaletteFilter();
    const visible = filter === "all"
      ? hardwarePaletteItems
      : hardwarePaletteItems.filter((item) => item.kind === filter);
    if (hardwarePaletteCount) {
      hardwarePaletteCount.textContent = `${visible.length}/${hardwarePaletteItems.length}`;
    }
    if (!hardwareEvidenceReport) {
      hardwarePaletteList.setAttribute("data-palette-state", "loading");
      hardwarePaletteList.textContent = "Hardware evidence loading. Truth effect: none.";
      return [];
    }
    if (!visible.length) {
      hardwarePaletteList.setAttribute("data-palette-state", "empty");
      hardwarePaletteList.textContent = "No matching hardware evidence items. Truth effect: none.";
      return [];
    }
    hardwarePaletteList.setAttribute("data-palette-state", "ready");
    hardwarePaletteList.innerHTML = visible.map((item) => [
      '<button',
      'type="button"',
      'class="workbench-hardware-palette-item"',
      `data-hardware-palette-id="${inspectorText(item.id)}"`,
      `data-palette-kind="${inspectorText(item.kind)}"`,
      `data-hardware-id="${inspectorText(item.binding.hardware_id)}"`,
      `aria-pressed="${item.id === selectedHardwarePaletteItemId ? "true" : "false"}"`,
      '>',
      `<strong>${inspectorText(item.label)}</strong>`,
      `<span>${inspectorText(item.detail)}</span>`,
      `<small>${inspectorText(item.source_ref || "hardware_evidence")}</small>`,
      `<em>${inspectorText(item.kind)} | ${inspectorText(item.status)}</em>`,
      '</button>',
    ].join(" ")).join("");
    return visible;
  }

  function currentHardwarePaletteAction() {
    return hardwarePaletteAction ? String(hardwarePaletteAction.value || "create-node") : "create-node";
  }

  function hardwarePaletteItemById(itemId) {
    return hardwarePaletteItems.find((item) => item.id === itemId) || null;
  }

  function addHardwarePaletteNode(item) {
    if (!item) return null;
    recordEditableHistory("hardware_palette_node");
    shell.setAttribute("data-draft-state", "derived");
    const nodeId = nextDraftNodeId();
    const node = createEditableNodeElement({
      id: nodeId,
      label: `Interface ${item.label}`,
      op: "and",
      ruleCount: "0",
      evidence: item.status === "recorded" || item.status === "confirmed" ? "ui_draft" : "evidence_gap",
      sourceRef: `ui_draft.hardware_palette.${item.kind}.${item.id}`,
      op_catalog_entry: "and",
      hardware_binding: hardwarePaletteBinding(item, "node", nodeId),
      port_contract: hardwarePalettePortContract(item, nodeId),
      x: `${36 + (nextDraftNodeIndex % 6) * 8}%`,
      y: `${24 + (nextDraftNodeIndex % 5) * 9}%`,
      draftNode: true,
    });
    refreshEditableNodes();
    if (node) selectNode(node);
    if (draftLabel) draftLabel.textContent = "sandbox_candidate hardware palette node pending";
    if (hardwarePaletteStatus) {
      hardwarePaletteStatus.textContent =
        `Created ${nodeId} from ${item.kind}:${item.label}. Sandbox evidence only; truth effect: none.`;
    }
    setTimelineState("derived");
    renderEditableEdges();
    validateEditableGraph();
    updateEditableDraftHash();
    persistDraft();
    return node;
  }

  function applyHardwarePaletteBinding(item) {
    if (!item) return null;
    const target = activeInterfaceBindingTarget();
    if (target.kind === "none") {
      if (hardwarePaletteStatus) {
        hardwarePaletteStatus.textContent = "Select a node or edge before applying hardware evidence. Truth effect: none.";
      }
      return null;
    }
    recordEditableHistory("hardware_palette_binding");
    const binding = hardwarePaletteBinding(item, target.kind, target.id);
    if (target.kind === "edge") {
      setEdgeInterfaceBinding(selectedEdge, binding);
      if (item.signal_id) {
        const existingContract = edgePortContract(selectedEdge);
        const nextContract = {
          ...existingContract,
          signal_id: item.signal_id,
          source_ref: item.source_ref || existingContract.source_ref || "ui_draft.hardware_palette.edge",
        };
        if (item.value_type && item.value_type !== "unknown") {
          nextContract.value_type = item.value_type;
        }
        setEdgePortContract(selectedEdge, nextContract);
      }
    } else if (target.kind === "node") {
      setNodeInterfaceBinding(selectedNode, binding);
    }
    if (draftLabel) draftLabel.textContent = "sandbox_candidate hardware palette binding pending";
    renderInspector();
    renderEditableEdges();
    if (hardwarePaletteStatus) {
      hardwarePaletteStatus.textContent =
        `Applied ${item.kind}:${item.label} to ${target.kind}:${target.id}. Sandbox evidence only; truth effect: none.`;
    }
    updateEditableDraftHash();
    persistDraft();
    return binding;
  }

  function handleHardwarePaletteItem(itemId) {
    selectedHardwarePaletteItemId = itemId;
    const item = hardwarePaletteItemById(itemId);
    if (!item) return null;
    const action = currentHardwarePaletteAction();
    const result = action === "apply-binding"
      ? applyHardwarePaletteBinding(item)
      : addHardwarePaletteNode(item);
    renderHardwarePalette();
    return result;
  }

  function buildHardwarePaletteSummary() {
    return {
      item_count: hardwarePaletteItems.length,
      selected_item_id: selectedHardwarePaletteItemId || null,
      action: currentHardwarePaletteAction(),
      source: "read_only_hardware_evidence_api",
      truth_effect: "none",
    };
  }

  function activeInterfaceBindingTarget() {
    if (selectedEdge) {
      return {
        kind: "edge",
        id: selectedEdge.id || `${selectedEdge.source || "unknown"}->${selectedEdge.target || "unknown"}`,
        binding: edgeInterfaceBinding(selectedEdge),
      };
    }
    if (selectedNode) {
      return {
        kind: "node",
        id: selectedNode.getAttribute("data-editable-node-id") || "unknown",
        binding: nodeInterfaceBinding(selectedNode),
      };
    }
    return {
      kind: "none",
      id: "none",
      binding: normalizeInterfaceBinding({}, "none", "none"),
    };
  }

  function formValueForInterfaceField(value) {
    return value && value !== "evidence_gap" ? value : "";
  }

  function setRuleEditorDisabledState(disabled) {
    for (const field of [ruleNameInput, ruleSourceSignalInput, ruleComparisonSelect, ruleThresholdInput]) {
      if (field) field.disabled = disabled;
    }
    if (applyRuleParameterBtn) applyRuleParameterBtn.disabled = disabled;
  }

  function defaultRuleForNode(node) {
    const nodeId = node && node.getAttribute("data-editable-node-id") || "unknown";
    const op = node && node.getAttribute("data-node-op") || "and";
    const portContract = nodePortContract(node);
    if (op === "between") {
      return normalizeNodeDraftRule({
        name: `${nodeId}_between_window`,
        source_signal_id: portContract.input_signal_id,
        comparison: "between_lower_inclusive",
        threshold_value: [-1, 1],
      }, nodeId);
    }
    if (op === "compare") {
      return normalizeNodeDraftRule({
        name: `${nodeId}_threshold`,
        source_signal_id: portContract.input_signal_id,
        comparison: ">=",
        threshold_value: 0,
      }, nodeId);
    }
    return normalizeNodeDraftRule({
      name: `${nodeId}_draft_rule`,
      source_signal_id: portContract.input_signal_id,
      comparison: "==",
      threshold_value: true,
    }, nodeId);
  }

  function renderRuleParameterEditor() {
    const target = activeInterfaceBindingTarget();
    const isNode = target.kind === "node" && selectedNode;
    setRuleEditorDisabledState(!isNode);
    if (ruleParameterOwner) {
      ruleParameterOwner.textContent = isNode ? `node:${target.id}` : `${target.kind}:${target.id}`;
    }
    const rule = isNode
      ? (nodeDraftRules(selectedNode)[0] || defaultRuleForNode(selectedNode))
      : normalizeNodeDraftRule({}, "none");
    if (ruleNameInput) ruleNameInput.value = rule.name;
    if (ruleSourceSignalInput) ruleSourceSignalInput.value = rule.source_signal_id;
    if (ruleComparisonSelect) ruleComparisonSelect.value = rule.comparison;
    if (ruleThresholdInput) ruleThresholdInput.value = ruleThresholdInputText(rule.threshold_value);
    if (ruleParameterStatus) {
      ruleParameterStatus.textContent = isNode
        ? `Editing sandbox rule for ${target.id}. Truth effect: none.`
        : "Select a node to edit sandbox rule parameters. Truth effect: none.";
    }
  }

  function readRuleParameterForm(node) {
    const nodeId = node && node.getAttribute("data-editable-node-id") || "unknown";
    return normalizeNodeDraftRule({
      name: ruleNameInput && ruleNameInput.value,
      source_signal_id: ruleSourceSignalInput && ruleSourceSignalInput.value,
      comparison: ruleComparisonSelect && ruleComparisonSelect.value,
      threshold_value: parseRuleThresholdValue(ruleThresholdInput && ruleThresholdInput.value),
    }, nodeId);
  }

  function applySelectedRuleParameter() {
    if (!selectedNode || selectedEdge) return null;
    recordEditableHistory("rule_parameter_edit");
    const rule = readRuleParameterForm(selectedNode);
    setNodeDraftRules(selectedNode, [rule]);
    if (draftLabel) draftLabel.textContent = "sandbox_candidate rule parameter edit pending";
    renderInspector();
    if (ruleParameterStatus) {
      ruleParameterStatus.textContent =
        `Applied rule ${rule.name} as local sandbox metadata. Truth effect: none.`;
    }
    updateEditableDraftHash();
    persistDraft();
    return rule;
  }

  function renderInterfaceBindingEditor() {
    const target = activeInterfaceBindingTarget();
    const binding = target.binding;
    const quality = interfaceBindingQualityReport(binding);
    if (interfaceBindingOwner) {
      interfaceBindingOwner.textContent = `${target.kind}:${target.id}`;
    }
    if (interfaceBindingQuality) {
      interfaceBindingQuality.textContent = quality.status;
      interfaceBindingQuality.setAttribute("data-binding-quality", quality.status);
    }
    if (interfaceHardwareIdInput) interfaceHardwareIdInput.value = formValueForInterfaceField(binding.hardware_id);
    if (interfaceCableInput) interfaceCableInput.value = formValueForInterfaceField(binding.cable);
    if (interfaceConnectorInput) interfaceConnectorInput.value = formValueForInterfaceField(binding.connector);
    if (interfacePortLocalInput) interfacePortLocalInput.value = formValueForInterfaceField(binding.port_local);
    if (interfacePortPeerInput) interfacePortPeerInput.value = formValueForInterfaceField(binding.port_peer);
    if (interfaceEvidenceStatusSelect) interfaceEvidenceStatusSelect.value = binding.evidence_status || "evidence_gap";
    if (interfaceBindingStatus) {
      interfaceBindingStatus.textContent =
        `Editing ${target.kind}:${target.id} as sandbox interface evidence. Truth effect: none.`;
    }
    if (interfaceBindingCoverage) {
      const missingText = quality.missing_fields.length
        ? ` Missing fields: ${quality.missing_fields.join(", ")}.`
        : " All required sandbox evidence fields are present.";
      interfaceBindingCoverage.textContent =
        `${quality.label}. ${missingText} Truth effect: none.`;
    }
  }

  function readInterfaceBindingForm(ownerKind, ownerId) {
    return normalizeInterfaceBinding({
      hardware_id: interfaceHardwareIdInput && interfaceHardwareIdInput.value,
      cable: interfaceCableInput && interfaceCableInput.value,
      connector: interfaceConnectorInput && interfaceConnectorInput.value,
      port_local: interfacePortLocalInput && interfacePortLocalInput.value,
      port_peer: interfacePortPeerInput && interfacePortPeerInput.value,
      evidence_status: interfaceEvidenceStatusSelect && interfaceEvidenceStatusSelect.value,
    }, ownerKind, ownerId);
  }

  function applySelectedInterfaceBinding() {
    const target = activeInterfaceBindingTarget();
    if (target.kind === "none") return null;
    recordEditableHistory("interface_binding_edit");
    const binding = readInterfaceBindingForm(target.kind, target.id);
    if (target.kind === "edge") {
      setEdgeInterfaceBinding(selectedEdge, binding);
    } else if (target.kind === "node") {
      setNodeInterfaceBinding(selectedNode, binding);
    }
    if (draftLabel) draftLabel.textContent = "sandbox_candidate interface binding edit pending";
    renderInspector();
    if (interfaceBindingStatus) {
      interfaceBindingStatus.textContent =
        `Applied ${target.kind}:${target.id} interface binding as local sandbox evidence. Truth effect: none.`;
    }
    renderEditableEdges();
    updateEditableDraftHash();
    persistDraft();
    return binding;
  }

  function setPortEditorDisabledState(targetKind) {
    const nodeFields = [portInputSignalInput, portOutputSignalInput];
    const edgeFields = [edgeSignalIdInput, edgeSourcePortInput, edgeTargetPortInput];
    for (const field of nodeFields) {
      if (field) field.disabled = targetKind !== "node";
    }
    for (const field of edgeFields) {
      if (field) field.disabled = targetKind !== "edge";
    }
    for (const field of [portValueTypeSelect, portUnitInput, portRequiredInput]) {
      if (field) field.disabled = targetKind === "none";
    }
  }

  function renderTypedPortEditor() {
    const target = activeInterfaceBindingTarget();
    setPortEditorDisabledState(target.kind);
    if (typedPortOwner) {
      typedPortOwner.textContent = `${target.kind}:${target.id}`;
    }
    if (target.kind === "edge") {
      const contract = edgePortContract(selectedEdge);
      if (portInputSignalInput) portInputSignalInput.value = "";
      if (portOutputSignalInput) portOutputSignalInput.value = "";
      if (edgeSignalIdInput) edgeSignalIdInput.value = contract.signal_id === "evidence_gap" ? "" : contract.signal_id;
      if (edgeSourcePortInput) edgeSourcePortInput.value = contract.source_port_id === "evidence_gap" ? "" : contract.source_port_id;
      if (edgeTargetPortInput) edgeTargetPortInput.value = contract.target_port_id === "evidence_gap" ? "" : contract.target_port_id;
      if (portValueTypeSelect) portValueTypeSelect.value = contract.value_type;
      if (portUnitInput) portUnitInput.value = contract.unit;
      if (portRequiredInput) portRequiredInput.checked = contract.required;
      if (portContractStatus) {
        portContractStatus.textContent =
          `Editing edge port metadata ${target.id}. Truth effect: none.`;
      }
      return;
    }
    if (target.kind === "node") {
      const contract = nodePortContract(selectedNode);
      if (portInputSignalInput) portInputSignalInput.value = contract.input_signal_id;
      if (portOutputSignalInput) portOutputSignalInput.value = contract.output_signal_id;
      if (edgeSignalIdInput) edgeSignalIdInput.value = "";
      if (edgeSourcePortInput) edgeSourcePortInput.value = "";
      if (edgeTargetPortInput) edgeTargetPortInput.value = "";
      if (portValueTypeSelect) portValueTypeSelect.value = contract.value_type;
      if (portUnitInput) portUnitInput.value = contract.unit;
      if (portRequiredInput) portRequiredInput.checked = contract.required;
      if (portContractStatus) {
        portContractStatus.textContent =
          `Editing node typed ports ${target.id}. Local sandbox contract only. Truth effect: none.`;
      }
      return;
    }
    if (portInputSignalInput) portInputSignalInput.value = "";
    if (portOutputSignalInput) portOutputSignalInput.value = "";
    if (edgeSignalIdInput) edgeSignalIdInput.value = "";
    if (edgeSourcePortInput) edgeSourcePortInput.value = "";
    if (edgeTargetPortInput) edgeTargetPortInput.value = "";
    if (portValueTypeSelect) portValueTypeSelect.value = "unknown";
    if (portUnitInput) portUnitInput.value = "";
    if (portRequiredInput) portRequiredInput.checked = false;
    if (portContractStatus) {
      portContractStatus.textContent = "Select a node or edge to edit sandbox ports. Truth effect: none.";
    }
  }

  function readPortContractForm(target) {
    const valueType = portValueTypeSelect && portValueTypeSelect.value;
    const unit = portUnitInput && portUnitInput.value;
    const required = Boolean(portRequiredInput && portRequiredInput.checked);
    if (target.kind === "edge") {
      return {
        source_port_id: edgeSourcePortInput && edgeSourcePortInput.value,
        target_port_id: edgeTargetPortInput && edgeTargetPortInput.value,
        signal_id: edgeSignalIdInput && edgeSignalIdInput.value,
        value_type: valueType,
        unit,
        required,
        truth_effect: "none",
      };
    }
    return normalizePortContract({
      input_signal_id: portInputSignalInput && portInputSignalInput.value,
      output_signal_id: portOutputSignalInput && portOutputSignalInput.value,
      value_type: valueType,
      unit,
      required,
      truth_effect: "none",
    }, target.id);
  }

  function applySelectedPortContract() {
    const target = activeInterfaceBindingTarget();
    if (target.kind === "none") return null;
    recordEditableHistory("port_contract_edit");
    const contract = readPortContractForm(target);
    if (target.kind === "edge") {
      setEdgePortContract(selectedEdge, contract);
    } else if (target.kind === "node") {
      setNodePortContract(selectedNode, contract);
    }
    if (draftLabel) draftLabel.textContent = "sandbox_candidate typed port edit pending";
    renderInspector();
    if (portContractStatus) {
      portContractStatus.textContent =
        `Applied ${target.kind}:${target.id} typed port metadata as sandbox evidence. Truth effect: none.`;
    }
    renderEditableEdges();
    validateEditableGraph();
    updateEditableDraftHash();
    persistDraft();
    return contract;
  }

  function renderEdgeInspector(edge) {
    const payload = edgeInspectorPayload(edge || {});
    if (nodeIdSlot) nodeIdSlot.textContent = payload.id;
    if (labelInput) labelInput.value = `${payload.source_node_id} -> ${payload.target_node_id}`;
    if (opSelect) opSelect.value = "and";
    if (ruleCountSlot) ruleCountSlot.textContent = "edge";
    if (evidenceSlot) evidenceSlot.textContent = payload.evidence_status;
    if (signalCountSlot) signalCountSlot.textContent = "1";
    if (sourceRefSlot) sourceRefSlot.textContent = `ui_draft.edges.${payload.id}`;
    if (!evidenceDetail) return;
    evidenceDetail.innerHTML = [
      '<dl class="workbench-inspector-edge-list">',
      '<div><dt>Source node</dt>',
      `<dd>${inspectorText(payload.source_node_id)}</dd></div>`,
      '<div><dt>Target node</dt>',
      `<dd>${inspectorText(payload.target_node_id)}</dd></div>`,
      '<div><dt>Source port</dt>',
      `<dd>${inspectorText(payload.source_port_id)}</dd></div>`,
      '<div><dt>Target port</dt>',
      `<dd>${inspectorText(payload.target_port_id)}</dd></div>`,
      '<div><dt>Source type</dt>',
      `<dd>${inspectorText(`${payload.source_port_direction}/${payload.source_port_value_type}`)}</dd></div>`,
      '<div><dt>Target type</dt>',
      `<dd>${inspectorText(`${payload.target_port_direction}/${payload.target_port_value_type}`)}</dd></div>`,
      '<div><dt>Signal</dt>',
      `<dd>${inspectorText(payload.signal_id)}</dd></div>`,
      '<div><dt>Edge label</dt>',
      `<dd>${inspectorText(payload.edge_label)}</dd></div>`,
      '<div><dt>Route mode</dt>',
      `<dd>${inspectorText(payload.route_metadata.routing_mode)}</dd></div>`,
      '<div><dt>Port compatibility</dt>',
      `<dd>${inspectorText(payload.port_compatibility_status)}</dd></div>`,
      '<div><dt>Validation</dt>',
      `<dd>${inspectorText(payload.validation_issue)}</dd></div>`,
      '</dl>',
      '<p class="workbench-inspector-truth-note">truth_effect: none</p>',
    ].join("");
    renderHardwareEvidenceV2Report(buildHardwareEvidenceV2Report(activeInterfaceBindingTarget(), []));
    renderSelectedDebugTimeline("selection");
    renderCandidateBaselineDiffReviewV2("selection");
    renderRuleParameterEditor();
    renderInterfaceBindingEditor();
    renderHardwareBindingDiagnostics();
    renderTypedPortEditor();
    renderSubsystemEditor();
  }

  function renderInspector() {
    if (selectedEdge) {
      renderEdgeInspector(selectedEdge);
      return;
    }
    const payload = selectedNodePayload();
    if (!payload) {
      if (nodeIdSlot) nodeIdSlot.textContent = "none";
      if (labelInput) labelInput.value = "";
      if (opSelect) opSelect.value = selectedCatalogOp;
      if (ruleCountSlot) ruleCountSlot.textContent = "0";
      if (evidenceSlot) evidenceSlot.textContent = "evidence_gap";
      if (sourceRefSlot) sourceRefSlot.textContent = "ui_draft.empty_canvas";
      if (evidenceDetail) {
        evidenceDetail.textContent = "Empty sandbox draft. Add a primitive node to inspect graph evidence.";
      }
      renderHardwareEvidenceV2Report(buildHardwareEvidenceV2Report(activeInterfaceBindingTarget(), []));
      renderSelectedDebugTimeline("empty_canvas");
      renderCandidateBaselineDiffReviewV2("empty_canvas");
      renderRuleParameterEditor();
      renderInterfaceBindingEditor();
      renderHardwareBindingDiagnostics();
      renderTypedPortEditor();
      renderSubsystemEditor();
      return;
    }
    if (nodeIdSlot) nodeIdSlot.textContent = payload.id;
    if (labelInput) labelInput.value = payload.label;
    if (opSelect) opSelect.value = payload.op;
    if (ruleCountSlot) ruleCountSlot.textContent = payload.ruleCount;
    if (evidenceSlot) evidenceSlot.textContent = payload.evidence;
    if (sourceRefSlot) sourceRefSlot.textContent = payload.sourceRef;
    renderInspectorEvidenceDetails(payload);
    renderHardwareEvidenceV2Report(buildHardwareEvidenceV2Report(
      activeInterfaceBindingTarget(),
      evidenceRowsForNode(hardwareEvidenceReport, payload.id),
    ));
    renderSelectedDebugTimeline("selection");
    renderCandidateBaselineDiffReviewV2("selection");
    renderRuleParameterEditor();
    renderInterfaceBindingEditor();
    renderHardwareBindingDiagnostics();
    renderTypedPortEditor();
    renderSubsystemEditor();
  }

  function selectEditableEdgeByIndex(edgeIndex, options) {
    if (!options || options.preserveDiagnosticFocus !== true) {
      selectedDiagnosticFocus = null;
    }
    selectedEdge = Number.isInteger(edgeIndex) ? draftEdges[edgeIndex] || null : null;
    if (!selectedEdge) return;
    selectedNode = null;
    selectedNodeIds = new Set();
    for (const candidate of nodes) {
      candidate.setAttribute("aria-pressed", "false");
      candidate.setAttribute("data-multi-selected", "false");
    }
    if (edgeSvg) {
      for (const path of Array.from(edgeSvg.querySelectorAll("[data-editable-edge-id]"))) {
        path.setAttribute(
          "aria-pressed",
          Number.parseInt(path.getAttribute("data-editable-edge-index") || "-1", 10) === edgeIndex ? "true" : "false",
        );
      }
    }
    recordCanvasInteractionAction("select_edge");
    renderEdgeInspector(selectedEdge);
    renderCandidateDebuggerView(currentCandidateDebuggerView("select_edge"));
    if (graphValidationStatus) {
      const payload = edgeInspectorPayload(selectedEdge);
      graphValidationStatus.textContent =
        `Graph validation: edge ${payload.id} source_port=${payload.source_port_id} target_port=${payload.target_port_id}.`;
    }
    updateEditableDraftHash();
    persistDraft();
  }

  function selectEditableEdge(edgeId, options) {
    const edgeIndex = draftEdges.findIndex((edge) => edge.id === edgeId);
    if (edgeIndex >= 0) selectEditableEdgeByIndex(edgeIndex, options);
  }

  function selectNode(node, options) {
    if (!options || options.preserveDiagnosticFocus !== true) {
      selectedDiagnosticFocus = null;
    }
    selectedEdge = null;
    const nodeId = node && node.getAttribute("data-editable-node-id") || "";
    if (currentEditorTool === "edge" && pendingEdgeSourceId && nodeId && nodeId !== pendingEdgeSourceId) {
      connectEditableEdge(pendingEdgeSourceId, nodeId);
      pendingEdgeSourceId = "";
      setEditorTool("select");
    } else if (currentEditorTool === "edge" && nodeId && !pendingEdgeSourceId) {
      pendingEdgeSourceId = nodeId;
      if (graphValidationStatus) {
        graphValidationStatus.textContent = `Graph validation: select target node for edge from ${nodeId}.`;
      }
    }
    if (options && options.multiSelect) {
      toggleEditableNodeSelection(node);
    } else {
      setSingleEditableNodeSelection(node);
    }
    if (edgeSvg) {
      for (const path of Array.from(edgeSvg.querySelectorAll("[data-editable-edge-id]"))) {
        path.setAttribute("aria-pressed", "false");
      }
    }
    renderInspector();
    renderCandidateDebuggerView(currentCandidateDebuggerView("select_node"));
    updateEditableDraftHash();
    validateEditableGraph();
    persistDraft();
  }

  function deriveDraft() {
    shell.setAttribute("data-draft-state", "derived");
    if (draftLabel) {
      draftLabel.textContent = "sandbox_candidate derived from reference sample";
    }
    setTimelineState("derived");
    updateEditableDraftHash();
    validateEditableGraph();
    persistDraft();
  }

  function restoreDraft() {
    try {
      const raw = window.localStorage.getItem(storageKey);
      if (!raw) return;
      const payload = JSON.parse(raw);
      if (!payload || typeof payload !== "object") return;
      if (payload.draftState === "derived") {
        shell.setAttribute("data-draft-state", "derived");
        if (draftLabel) {
          draftLabel.textContent = "sandbox_candidate restored from browser draft";
        }
        setTimelineState("derived");
      }
      applyEditableState({
        draftState: payload.draftState || "baseline",
        canvasAuthoringMode: payload.canvasAuthoringMode || payload.canvas_authoring_mode || "reference_sample",
        selectedNodeId: payload.selectedNodeId,
        selectedNodeIds: Array.isArray(payload.selectedNodeIds) ? payload.selectedNodeIds : [],
        diagnosticFocus: payload.diagnosticFocus || null,
        repairActionLog: payload.repairActionLog || payload.repair_action_log || [],
        viewportState: payload.viewportState || defaultViewportState(),
        workspaceDocument: payload.workspaceDocument || payload.workspace_document || null,
        canvasInteractionSummary: payload.canvasInteractionSummary || payload.canvas_interaction_summary || null,
        sandboxTestBench: payload.sandboxTestBench || payload.sandbox_test_bench || null,
        sandboxTestRunReport: payload.sandboxTestRunReport || payload.sandbox_test_run_report || null,
        selectedCatalogOp: payload.selectedCatalogOp,
        subsystemGroups: payload.subsystemGroups || payload.subsystem_groups || [],
        capturedSubsystemTemplates: (
          payload.capturedSubsystemTemplates
          || payload.captured_subsystem_templates
          || payload.capturedTemplates
          || payload.captured_templates
          || []
        ),
        nodes: Array.isArray(payload.nodes) ? payload.nodes : [],
        edges: Array.isArray(payload.edges) ? payload.edges : draftEdges,
      });
    } catch (_err) {
      // Bad browser draft should not break first paint.
    }
  }

  function hydrateEvidenceSummary() {
    if (!evidenceSummary) return;
    const endpoint = evidenceSummary.getAttribute("data-evidence-api");
    if (!endpoint || typeof fetch !== "function") return;
    fetch(endpoint, { headers: { Accept: "application/json" } })
      .then((response) => response.ok ? response.json() : null)
      .then((payload) => {
        if (!payload || !payload.coverage || !payload.evidence_gaps) return;
        hardwareEvidenceReport = payload;
        const lru = payload.coverage.lru_inventory.actual_count;
        const bindings = payload.coverage.signal_bindings.actual_count;
        const gaps = payload.evidence_gaps.total_field_count;
        evidenceSummary.textContent =
          `Read-only evidence: ${lru} LRUs, ${bindings} signal bindings, ${gaps} evidence-gap fields.`;
        renderHardwarePalette();
        renderInspectorEvidenceDetails(selectedNodePayload());
        renderHardwareEvidenceV2Report(currentHardwareEvidenceV2Report());
      })
      .catch(() => {
        evidenceSummary.textContent = "Hardware evidence API unavailable; draft editing still remains sandbox-only.";
        renderHardwarePalette();
        renderHardwareEvidenceV2Report(currentHardwareEvidenceV2Report());
      });
  }

  function editableDraftHash(text) {
    let hash = 2166136261;
    for (let index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return `ui_draft_${(hash >>> 0).toString(16).padStart(8, "0")}`;
  }

  function currentDraftSnapshot() {
    const selected = selectedNodePayload() || {};
    const hardwareBindings = collectWorkbenchHardwareBindings();
    const bindingCoverage = buildInterfaceBindingCoverageSummary(hardwareBindings);
    const hardwareBindingDiagnostics = buildHardwareBindingDiagnosticsReport(hardwareBindings);
    const typedPorts = collectWorkbenchTypedPorts();
    const interfacePorts = collectWorkbenchInterfacePorts();
    const portContractSummary = buildPortContractSummary(typedPorts, draftEdges);
    const portCompatibilityReport = buildPortCompatibilityReport(typedPorts, draftEdges);
    const interfaceMatrix = buildWorkbenchInterfaceMatrix(
      hardwareBindings,
      typedPorts,
      hardwareBindingDiagnostics,
      bindingCoverage,
    );
    const connectorPinMap = buildWorkbenchConnectorPinMap(hardwareBindings);
    const operationCatalog = buildOperationCatalogSummary();
    const componentLibrary = buildComponentLibrarySummary();
    const subsystemGroupSummary = subsystemGroupsSnapshot();
    const subsystemInterfaceContracts = buildSubsystemInterfaceContractsSummary(subsystemGroupSummary);
    const ruleParameterSummary = buildRuleParameterSummary();
    const hardwarePalette = buildHardwarePaletteSummary();
    const hardwareEvidenceV2 = currentHardwareEvidenceV2Report();
    const selectedDebugTimeline = currentSelectedDebugTimelinePacket("snapshot");
    const candidateBaselineDiffReviewV2 = currentCandidateBaselineDiffReviewV2Report("snapshot");
    const sandboxTestBench = safeSandboxTestBenchDefinition();
    const sandboxTestRunReport = currentSandboxTestRunReport();
    const candidateDebuggerView = currentCandidateDebuggerView("snapshot");
    const preflightAnalyzerReport = currentPreflightAnalyzerReport("snapshot");
    const hardwareInterfaceDesigner = currentHardwareInterfaceDesignerPayload("snapshot");
    const hardwareInterfaceDesignerValidation =
      currentHardwareInterfaceDesignerValidationReport("snapshot");
    const diagnosticRepairActions = repairActionLogSnapshot();
    const workspaceDocument = currentWorkspaceDocument();
    const canvasInteractionSummary = currentCanvasInteractionSummary();
    const snapshot = {
      draft_state: shell.getAttribute("data-draft-state") || "baseline",
      canvas_authoring_mode: canvasAuthoringMode,
      system_id: "thrust-reverser",
      baseline_adapter: "reference-deploy-controller",
      truth_level_impact: "none",
      dal_pssa_impact: "none",
      controller_truth_modified: false,
      workspace_document: workspaceDocument,
      canvas_interaction_summary: canvasInteractionSummary,
      diagnostic_focus: currentDiagnosticFocusSummary(),
      viewport_state: viewportStateSnapshot(),
      selected_node: selected,
      selected_node_ids: Array.from(selectedNodeIds),
      nodes: nodes.map((node) => editableNodeState(node)),
      ports: [...typedPorts, ...interfacePorts],
      typed_ports: typedPorts,
      edges: draftEdges.map((edge) => ({
        ...edge,
        ...edgeInspectorPayload(edge),
        hardware_binding: edgeInterfaceBinding(edge),
      })),
      hardware_bindings: hardwareBindings,
      binding_coverage: bindingCoverage,
      hardware_binding_diagnostics: hardwareBindingDiagnostics,
      interface_matrix: interfaceMatrix,
      interface_matrix_validation: lastInterfaceMatrixValidationReport,
      connector_pin_map: connectorPinMap,
      repair_action_log: diagnosticRepairActions,
      port_contract_summary: portContractSummary,
      port_compatibility_report: portCompatibilityReport,
      operation_catalog: operationCatalog,
      component_library: componentLibrary,
      subsystem_groups: subsystemGroupSummary,
      subsystem_interface_contracts: subsystemInterfaceContracts,
      rule_parameter_summary: ruleParameterSummary,
      hardware_palette: hardwarePalette,
      hardware_evidence_v2: hardwareEvidenceV2,
      selected_debug_timeline: selectedDebugTimeline,
      candidate_baseline_diff_review_v2: candidateBaselineDiffReviewV2,
      sandbox_test_bench: sandboxTestBench,
      sandbox_test_run_report: sandboxTestRunReport,
      candidate_debugger_view: candidateDebuggerView,
      preflight_analyzer_report: preflightAnalyzerReport,
      hardware_interface_designer: hardwareInterfaceDesigner,
      hardware_interface_designer_validation: hardwareInterfaceDesignerValidation,
    };
    snapshot.editable_graph_document = buildEditableGraphDocumentFromSnapshot(snapshot);
    return snapshot;
  }

  function uniqueSourceRefs() {
    const refs = [];
    for (const node of nodes) {
      const ref = node.getAttribute("data-source-ref") || "";
      if (ref && refs.indexOf(ref) === -1) refs.push(ref);
    }
    return refs;
  }

  function selectedWorkbenchScenarioId() {
    return (scenarioSelect && scenarioSelect.value) || "nominal_landing";
  }

  function parseWorkbenchCustomSnapshot() {
    if (!customSnapshotInput) return null;
    const raw = String(customSnapshotInput.value || "").trim();
    if (!raw || raw === "{}") return null;
    const payload = JSON.parse(raw);
    if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
      throw new Error("custom snapshot JSON must be an object");
    }
    return payload;
  }

  function safeWorkbenchCustomSnapshot() {
    try {
      return parseWorkbenchCustomSnapshot();
    } catch (_err) {
      return null;
    }
  }

  function currentWorkbenchScenarioMetadata() {
    const customSnapshot = safeWorkbenchCustomSnapshot() || {};
    const rawSnapshot = customSnapshotInput ? String(customSnapshotInput.value || "").trim() : "";
    return {
      scenario_id: selectedWorkbenchScenarioId(),
      custom_snapshot_applied: Boolean((rawSnapshot && rawSnapshot !== "{}") || Object.keys(customSnapshot).length > 0),
      custom_snapshot_keys: Object.keys(customSnapshot).sort(),
      custom_snapshot_truth_effect: "none",
    };
  }

  function parseSandboxTestBenchArray(input, fallback, label) {
    const raw = input ? String(input.value || "").trim() : "";
    if (!raw) return fallback;
    const payload = JSON.parse(raw);
    if (!Array.isArray(payload)) {
      throw new Error(`${label} JSON must be an array`);
    }
    return payload;
  }

  function normalizeSandboxTickRecord(record, fallbackIndex) {
    if (!record || typeof record !== "object" || Array.isArray(record)) {
      throw new Error(`scenario tick ${fallbackIndex || 0} must be an object`);
    }
    const tick = Number.isFinite(Number(record.tick)) ? Number(record.tick) : fallbackIndex || 0;
    const inputs = record.inputs && typeof record.inputs === "object" && !Array.isArray(record.inputs)
      ? normalizeEvidenceArchiveValue(record.inputs)
      : {};
    return {
      tick,
      inputs,
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    };
  }

  function normalizeSandboxAssertionRecord(record, fallbackIndex) {
    if (!record || typeof record !== "object" || Array.isArray(record)) {
      throw new Error(`scenario assertion ${fallbackIndex || 0} must be an object`);
    }
    const target = String(record.target || record.port_id || record.signal_id || "").trim();
    if (!target) throw new Error(`scenario assertion ${fallbackIndex || 0} target is required`);
    return {
      tick: Number.isFinite(Number(record.tick)) ? Number(record.tick) : 0,
      target,
      expected: normalizeEvidenceArchiveValue(record.expected),
      comparator: String(record.comparator || "equals"),
      candidate_state: "sandbox_candidate",
      truth_effect: "none",
    };
  }

  function currentSandboxTestBenchDefinition() {
    const tickRecords = parseSandboxTestBenchArray(
      sandboxTestBenchInputs,
      [{ tick: 0, inputs: {} }],
      "scenario inputs",
    ).map((record, index) => normalizeSandboxTickRecord(record, index));
    const assertionRecords = parseSandboxTestBenchArray(
      sandboxTestBenchAssertions,
      [],
      "scenario assertions",
    ).map((record, index) => normalizeSandboxAssertionRecord(record, index));
    return {
      kind: sandboxTestBenchKind,
      version: sandboxTestBenchVersion,
      scenario_id: selectedWorkbenchScenarioId(),
      ticks: tickRecords,
      assertions: assertionRecords,
      tick_count: tickRecords.length,
      assertion_count: assertionRecords.length,
      source: "browser_local_draft",
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_effect: "none",
    };
  }

  function fallbackSandboxTestBenchDefinition(errorMessage) {
    return {
      kind: sandboxTestBenchKind,
      version: sandboxTestBenchVersion,
      scenario_id: selectedWorkbenchScenarioId(),
      ticks: [],
      assertions: [],
      tick_count: 0,
      assertion_count: 0,
      validation_error: String(errorMessage || "invalid sandbox test bench JSON"),
      source: "browser_local_draft",
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_effect: "none",
    };
  }

  function safeSandboxTestBenchDefinition() {
    try {
      return currentSandboxTestBenchDefinition();
    } catch (err) {
      return fallbackSandboxTestBenchDefinition(err && err.message ? err.message : "invalid sandbox test bench JSON");
    }
  }

  function restoreSandboxTestBenchDefinition(definition) {
    if (!definition || typeof definition !== "object" || Array.isArray(definition)) return;
    if (sandboxTestBenchInputs && Array.isArray(definition.ticks)) {
      sandboxTestBenchInputs.value = JSON.stringify(
        definition.ticks.map((tick) => ({
          tick: tick.tick,
          inputs: tick.inputs || {},
        })),
        null,
        2,
      );
    }
    if (sandboxTestBenchAssertions && Array.isArray(definition.assertions)) {
      sandboxTestBenchAssertions.value = JSON.stringify(
        definition.assertions.map((assertion) => ({
          tick: assertion.tick,
          target: assertion.target,
          expected: assertion.expected,
          comparator: assertion.comparator || "equals",
        })),
        null,
        2,
      );
    }
  }

  function normalizeImportedSandboxTestRunReport(report) {
    if (!report || typeof report !== "object" || Array.isArray(report)) return null;
    return {
      ...report,
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_effect: "none",
    };
  }

  function currentSandboxTestRunReport() {
    return normalizeImportedSandboxTestRunReport(lastSandboxTestRunReport);
  }

  function candidateDebuggerTargetContext() {
    if (selectedEdge) {
      const payload = edgeInspectorPayload(selectedEdge);
      const binding = edgeInterfaceBinding(selectedEdge);
      const portIds = [
        payload.source_port_id,
        payload.target_port_id,
        `${payload.source_node_id}:out`,
        `${payload.target_node_id}:in`,
      ].filter(Boolean);
      return {
        kind: "edge",
        id: payload.id,
        owner_key: `edge:${payload.id}`,
        label: payload.edge_label || `${payload.source_node_id}->${payload.target_node_id}`,
        port_ids: Array.from(new Set(portIds)),
        hardware_binding: normalizeInterfaceBinding(binding, "edge", payload.id),
        truth_effect: "none",
      };
    }
    const payload = selectedNodePayload() || {};
    const nodeId = payload.id || "unknown";
    const contract = normalizePortContract(payload.port_contract || {}, nodeId);
    const binding = payload.hardware_binding || normalizeInterfaceBinding({}, "node", nodeId);
    const portIds = [
      contract.output_port_id,
      `${nodeId}:out`,
      contract.input_port_id,
      `${nodeId}:in`,
      nodeId,
    ].filter(Boolean);
    return {
      kind: "node",
      id: nodeId,
      owner_key: `node:${nodeId}`,
      label: payload.label || nodeId,
      port_ids: Array.from(new Set(portIds)),
      hardware_binding: normalizeInterfaceBinding(binding, "node", nodeId),
      truth_effect: "none",
    };
  }

  function debuggerAssertionMatchesTarget(assertion, target) {
    const assertionTarget = String((assertion && assertion.target) || "");
    if (!assertionTarget || !target) return false;
    return assertionTarget === target.id
      || assertionTarget === target.owner_key
      || (target.port_ids || []).includes(assertionTarget);
  }

  function firstDebuggerAssertion(report, target) {
    const assertions = Array.isArray(report && report.assertions) ? report.assertions : [];
    return assertions.find((assertion) => (
      assertion.status === "fail" && debuggerAssertionMatchesTarget(assertion, target)
    )) || assertions.find((assertion) => assertion.status === "fail") || null;
  }

  function debuggerTraceFrame(report, tick) {
    const trace = Array.isArray(report && report.trace) ? report.trace : [];
    if (tick !== null && tick !== undefined) {
      const selected = trace.find((frame) => Number(frame.tick) === Number(tick));
      if (selected) return selected;
    }
    return trace[0] || null;
  }

  function debuggerObservedValues(frame, target) {
    const values = frame && frame.values && typeof frame.values === "object" ? frame.values : {};
    return (target.port_ids || []).map((portId) => {
      const observed = readSandboxValue(values, [portId]);
      return {
        port_id: portId,
        value: normalizeEvidenceArchiveValue(observed),
        available: observed !== undefined,
        truth_effect: "none",
      };
    });
  }

  function formatDebuggerValue(value) {
    if (value === undefined) return "unavailable";
    if (typeof value === "string") return value;
    return stableEvidenceArchiveJson(value);
  }

  function formatDebuggerAssertion(assertion) {
    if (!assertion) return "not run";
    return [
      assertion.target || "unknown",
      `tick=${assertion.tick}`,
      `expected=${formatDebuggerValue(assertion.expected)}`,
      `observed=${formatDebuggerValue(assertion.observed)}`,
      assertion.status || "unknown",
    ].join(" ");
  }

  function formatDebuggerObserved(values) {
    const available = (values || []).filter((item) => item.available);
    if (!available.length) return "unavailable";
    return available
      .map((item) => `${item.port_id}=${formatDebuggerValue(item.value)}`)
      .join(" · ");
  }

  function currentCandidateDebuggerView(state) {
    const target = candidateDebuggerTargetContext();
    const report = currentSandboxTestRunReport();
    const firstFail = firstDebuggerAssertion(report, target);
    const selectedTick = firstFail
      ? Number(firstFail.tick)
      : (
        report && Array.isArray(report.trace) && report.trace[0]
          ? Number(report.trace[0].tick)
          : null
      );
    const frame = debuggerTraceFrame(report, selectedTick);
    const observedValues = frame ? debuggerObservedValues(frame, target) : [];
    return {
      kind: candidateDebuggerViewKind,
      version: candidateDebuggerViewVersion,
      workflow_state: state || "selection",
      target,
      status: report ? (report.status || "not_run") : "not_run",
      scenario_id: report ? (report.scenario_id || selectedWorkbenchScenarioId()) : selectedWorkbenchScenarioId(),
      assertion_status: report ? (report.assertion_status || "not_run") : "not_run",
      selected_tick: selectedTick,
      trace_available: Boolean(frame),
      trace_frame_count: report && Array.isArray(report.trace) ? report.trace.length : 0,
      first_failing_assertion: firstFail ? normalizeEvidenceArchiveValue(firstFail) : null,
      observed_values: observedValues,
      report_model_hash: report ? (report.model_hash || "unavailable") : "not_run",
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_effect: "none",
    };
  }

  function renderCandidateDebuggerView(view) {
    const packet = view || currentCandidateDebuggerView("render");
    const status = packet.status || "not_run";
    if (candidateDebuggerPanel) candidateDebuggerPanel.setAttribute("data-debugger-status", status);
    if (candidateDebuggerStatus) candidateDebuggerStatus.textContent = status;
    if (candidateDebuggerTarget) candidateDebuggerTarget.textContent = packet.target.owner_key || "none:none";
    if (candidateDebuggerTick) {
      candidateDebuggerTick.textContent =
        packet.selected_tick === null || packet.selected_tick === undefined
          ? "not_run"
          : String(packet.selected_tick);
    }
    if (candidateDebuggerAssertion) {
      candidateDebuggerAssertion.textContent = formatDebuggerAssertion(packet.first_failing_assertion);
    }
    if (candidateDebuggerObserved) {
      candidateDebuggerObserved.textContent = formatDebuggerObserved(packet.observed_values);
    }
    if (candidateDebuggerTrace) {
      candidateDebuggerTrace.textContent = packet.trace_available ? "available" : "unavailable";
    }
    return packet;
  }

  function normalizeImportedPreflightAnalyzerReport(report) {
    if (!report || typeof report !== "object" || Array.isArray(report)) return null;
    return {
      ...report,
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_effect: "none",
    };
  }

  function preflightCandidateModelSnapshot() {
    refreshEditableNodes();
    return {
      nodes: nodes.map((node) => editableNodeState(node)),
      edges: draftEdges.map((edge) => ({
        ...edge,
        ...edgeInspectorPayload(edge),
        hardware_binding: edgeInterfaceBinding(edge),
      })),
    };
  }

  function sandboxModelHashPayload(nodesForRun, edgesForRun, definition) {
    return {
      nodes: (nodesForRun || []).map((node) => ({
        id: node && node.id,
        op: node && (node.op_catalog_entry || node.op || node.opCatalogEntry || "and"),
        rules: node && Array.isArray(node.rules) ? node.rules : [],
        port_contract: node && (node.port_contract || node.portContract || null),
      })),
      edges: (edgesForRun || []).map((edge) => ({
        id: edge && edge.id,
        source: edge && edge.source,
        target: edge && edge.target,
        signal_id: edge && (edge.signal_id || edge.signalId || ""),
        source_port_id: edge && (edge.source_port_id || edge.sourcePortId || ""),
        target_port_id: edge && (edge.target_port_id || edge.targetPortId || ""),
        value_type: edge && (edge.value_type || edge.valueType || "boolean"),
        required: Boolean(edge && edge.required),
      })),
      definition,
    };
  }

  function sandboxCandidateModelHash(nodesForRun, edgesForRun, definition) {
    return editableDraftHash(stableEvidenceArchiveJson(
      sandboxModelHashPayload(nodesForRun, edgesForRun, definition),
    ));
  }

  function currentPreflightCandidateModelHash(definition) {
    const model = preflightCandidateModelSnapshot();
    const testBench = definition || safeSandboxTestBenchDefinition();
    return sandboxCandidateModelHash(model.nodes, model.edges, testBench);
  }

  function preflightFinding(code, severity, message, action) {
    return {
      code,
      severity,
      message,
      action,
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_effect: "none",
    };
  }

  function dedupePreflightActions(findings) {
    const actions = [];
    for (const finding of findings || []) {
      if (finding && finding.action && actions.indexOf(finding.action) === -1) {
        actions.push(finding.action);
      }
    }
    return actions.length ? actions : ["Candidate preflight is ready for review packet generation."];
  }

  function buildWorkbenchPreflightAnalyzerReport(state) {
    const testBench = safeSandboxTestBenchDefinition();
    const candidateModelHash = currentPreflightCandidateModelHash(testBench);
    const sandboxReport = currentSandboxTestRunReport();
    const graphIssues = validateEditableGraph();
    const hardwareBindings = collectWorkbenchHardwareBindings();
    const hardwareDiagnostics = buildHardwareBindingDiagnosticsReport(hardwareBindings);
    const typedPorts = collectWorkbenchTypedPorts();
    const portCompatibilityReport = buildPortCompatibilityReport(typedPorts, draftEdges);
    const candidateDebuggerView = currentCandidateDebuggerView("preflight");
    const hardwareInterfaceDesigner = currentHardwareInterfaceDesignerPayload("preflight");
    const hardwareInterfaceDesignerValidation =
      currentHardwareInterfaceDesignerValidationReport("preflight");
    const findings = [];

    for (const issue of graphIssues) {
      findings.push(preflightFinding(
        "graph_validation_failed",
        "error",
        `Graph validation issue: ${issue}`,
        "Fix dangling ports or duplicate graph edges.",
      ));
    }
    if (!sandboxReport) {
      findings.push(preflightFinding(
        "sandbox_test_missing",
        "warning",
        "No current sandbox test run report is available.",
        "Run sandbox scenario tests before handoff.",
      ));
    } else if (sandboxReport.model_hash !== candidateModelHash) {
      findings.push(preflightFinding(
        "stale_sandbox_test_run_report",
        "warning",
        "Sandbox test run report does not match the current candidate model hash.",
        "Rerun sandbox scenario tests for the current draft.",
      ));
    } else if (sandboxReport.status === "invalid_scenario" || (sandboxReport.unsupported_ops || []).length) {
      findings.push(preflightFinding(
        "invalid_sandbox_scenario",
        "error",
        "Sandbox scenario is invalid or contains unsupported operations.",
        "Fix invalid scenario inputs or unsupported operations.",
      ));
    } else if (sandboxReport.status === "fail" || sandboxReport.assertion_status === "fail") {
      findings.push(preflightFinding(
        "sandbox_test_failed",
        "error",
        "Sandbox scenario assertions failed.",
        "Fix failing sandbox assertions before handoff.",
      ));
    }
    if ((hardwareDiagnostics.evidence_gap_field_count || 0) > 0) {
      findings.push(preflightFinding(
        "hardware_evidence_gap",
        "warning",
        `${hardwareDiagnostics.evidence_gap_field_count} hardware/interface evidence gap field(s) remain.`,
        "Record hardware/interface evidence gaps before review.",
      ));
    }
    if (hardwareInterfaceDesignerValidation.status === "fail") {
      findings.push(preflightFinding(
        "hardware_interface_designer_invalid",
        "error",
        "Hardware/interface designer validation failed.",
        "Fix hardware/interface design records before ChangeRequest handoff.",
      ));
    } else if (hardwareInterfaceDesignerValidation.status === "warn") {
      findings.push(preflightFinding(
        "hardware_interface_designer_needs_evidence",
        "warning",
        "Hardware/interface designer has open evidence warnings.",
        "Resolve or explicitly archive hardware/interface evidence gaps.",
      ));
    }
    if ((portCompatibilityReport.error_count || 0) > 0) {
      findings.push(preflightFinding(
        "port_compatibility_error",
        "error",
        `${portCompatibilityReport.error_count} port compatibility error(s) remain.`,
        "Fix incompatible port links.",
      ));
    }
    const hasError = findings.some((finding) => finding.severity === "error");
    const classification = hasError
      ? "invalid_candidate"
      : (findings.length ? "needs_evidence" : "ready");
    return {
      kind: preflightAnalyzerReportKind,
      version: preflightAnalyzerReportVersion,
      workflow_state: state || "manual",
      classification,
      candidate_model_hash: candidateModelHash,
      sandbox_report_freshness: (
        !sandboxReport ? "missing" : (sandboxReport.model_hash === candidateModelHash ? "current" : "stale")
      ),
      findings,
      finding_count: findings.length,
      required_actions: dedupePreflightActions(findings),
      graph_validation_issues: graphIssues,
      hardware_binding_diagnostics: hardwareDiagnostics,
      hardware_interface_designer: hardwareInterfaceDesigner,
      hardware_interface_designer_validation: hardwareInterfaceDesignerValidation,
      port_compatibility_report: portCompatibilityReport,
      sandbox_test_bench: testBench,
      sandbox_test_run_report: sandboxReport,
      candidate_debugger_view: candidateDebuggerView,
      red_line_risks: [],
      live_linear_mutation: false,
      controller_truth_modified: false,
      frozen_assets_modified: false,
      truth_level_impact: "none",
      dal_pssa_impact: "none",
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_effect: "none",
    };
  }

  function currentPreflightAnalyzerReport(state) {
    const imported = normalizeImportedPreflightAnalyzerReport(lastPreflightAnalyzerReport);
    const candidateModelHash = currentPreflightCandidateModelHash();
    if (imported && imported.candidate_model_hash === candidateModelHash) {
      return {
        ...imported,
        workflow_state: state || imported.workflow_state || "current",
        candidate_state: "sandbox_candidate",
        certification_claim: "none",
        truth_effect: "none",
      };
    }
    return buildWorkbenchPreflightAnalyzerReport(state || "derived");
  }

  function renderWorkbenchPreflightAnalyzerReport(report) {
    const packet = normalizeImportedPreflightAnalyzerReport(report)
      || buildWorkbenchPreflightAnalyzerReport("render");
    lastPreflightAnalyzerReport = packet;
    const classification = packet.classification || "needs_evidence";
    if (preflightPanel) preflightPanel.setAttribute("data-preflight-classification", classification);
    if (preflightClassification) preflightClassification.textContent = classification;
    if (preflightFindingsCount) preflightFindingsCount.textContent = String(packet.finding_count || 0);
    if (preflightActions) preflightActions.textContent = (packet.required_actions || []).join(" · ");
    if (preflightOutput) preflightOutput.value = JSON.stringify(packet, null, 2);
    if (handoffStatus) {
      handoffStatus.textContent =
        `Preflight ${classification}. Truth effect: none. No certification claim.`;
    }
    return packet;
  }

  function runWorkbenchPreflightAnalyzer() {
    if (runPreflightBtn) runPreflightBtn.disabled = true;
    let report = null;
    try {
      report = buildWorkbenchPreflightAnalyzerReport("manual");
    } finally {
      if (runPreflightBtn) runPreflightBtn.disabled = false;
    }
    recordWorkspaceAction("run_preflight_analyzer");
    recordCanvasInteractionAction("run_preflight_analyzer");
    renderWorkspaceDocumentStatus();
    renderWorkbenchPreflightAnalyzerReport(report);
    persistDraft();
    return report;
  }

  function sandboxValueEquals(left, right) {
    return stableEvidenceArchiveJson(left) === stableEvidenceArchiveJson(right);
  }

  function sandboxBoolean(value) {
    if (typeof value === "boolean") return value;
    if (typeof value === "number") return value !== 0;
    if (typeof value === "string") {
      const normalized = value.trim().toLowerCase();
      return normalized === "true" || normalized === "1" || normalized === "yes";
    }
    return Boolean(value);
  }

  function sandboxNumber(value) {
    const numberValue = Number(value);
    return Number.isFinite(numberValue) ? numberValue : 0;
  }

  function nodeRuleThreshold(node, fallback) {
    const rules = Array.isArray(node && node.rules) ? node.rules : [];
    for (const rule of rules) {
      if (!rule || typeof rule !== "object") continue;
      const threshold = rule.threshold_value !== undefined ? rule.threshold_value : rule.threshold;
      if (threshold !== undefined && Number.isFinite(Number(threshold))) {
        return Number(threshold);
      }
    }
    return fallback;
  }

  function compareSandboxNumber(value, comparison, threshold) {
    const left = sandboxNumber(value);
    const right = sandboxNumber(threshold);
    if (comparison === "!=") return left !== right;
    if (comparison === "<") return left < right;
    if (comparison === "<=") return left <= right;
    if (comparison === ">") return left > right;
    if (comparison === ">=") return left >= right;
    return left === right;
  }

  function nodeRuleComparison(node, fallback) {
    const rules = Array.isArray(node && node.rules) ? node.rules : [];
    const rule = rules.find((item) => item && typeof item === "object" && item.comparison);
    return rule ? normalizeRuleComparison(rule.comparison) : fallback;
  }

  function nodeInputPortId(node) {
    const contract = node && (node.port_contract || node.portContract);
    return normalizePortContract(contract, node && node.id).input_port_id;
  }

  function nodeOutputPortId(node) {
    const contract = node && (node.port_contract || node.portContract);
    return normalizePortContract(contract, node && node.id).output_port_id;
  }

  function readSandboxValue(values, keys) {
    for (const key of keys || []) {
      if (key && Object.prototype.hasOwnProperty.call(values, key)) return values[key];
    }
    return undefined;
  }

  function nodeInputValues(node, values, edges) {
    const nodeId = String((node && node.id) || "");
    const candidates = [
      nodeInputPortId(node),
      `${nodeId}:in`,
      nodeId,
    ];
    const directValue = readSandboxValue(values, candidates);
    const incoming = (edges || [])
      .filter((edge) => edge && edge.target === nodeId)
      .map((edge) => readSandboxValue(values, [
        edge.target_port_id,
        edge.targetPortId,
        `${nodeId}:in`,
        edge.source_port_id,
        edge.sourcePortId,
        `${edge.source}:out`,
        edge.source,
      ]))
      .filter((value) => value !== undefined);
    if (directValue !== undefined) incoming.unshift(directValue);
    return incoming;
  }

  function writeSandboxNodeOutput(values, node, value) {
    const nodeId = String((node && node.id) || "");
    const outputPort = nodeOutputPortId(node);
    values[nodeId] = value;
    values[`${nodeId}:out`] = value;
    if (outputPort) values[outputPort] = value;
  }

  function propagateSandboxEdges(values, edges) {
    for (const edge of edges || []) {
      if (!edge) continue;
      const value = readSandboxValue(values, [
        edge.source_port_id,
        edge.sourcePortId,
        `${edge.source}:out`,
        edge.source,
      ]);
      if (value === undefined) continue;
      if (edge.target_port_id) values[edge.target_port_id] = value;
      if (edge.targetPortId) values[edge.targetPortId] = value;
      if (edge.target) values[`${edge.target}:in`] = value;
    }
  }

  function evaluateSandboxNode(node, inputValues, state) {
    const op = String((node && (node.op_catalog_entry || node.op || node.opCatalogEntry)) || "and");
    const values = inputValues.length ? inputValues : [false];
    if (!approvedOperationCatalog[op]) {
      return {
        status: "invalid",
        value: null,
        finding: {
          code: "unsupported_op",
          node_id: node && node.id,
          op,
          message: `Unsupported sandbox op ${op}`,
          truth_effect: "none",
        },
      };
    }
    if (op === "or") return { status: "ok", value: values.some((value) => sandboxBoolean(value)) };
    if (op === "compare") {
      return {
        status: "ok",
        value: compareSandboxNumber(
          values[0],
          nodeRuleComparison(node, ">="),
          nodeRuleThreshold(node, 5),
        ),
      };
    }
    if (op === "between") {
      const rules = Array.isArray(node && node.rules) ? node.rules : [];
      const thresholds = rules
        .map((rule) => rule && (rule.threshold_value !== undefined ? rule.threshold_value : rule.threshold))
        .filter((value) => Number.isFinite(Number(value)))
        .map((value) => Number(value));
      const lower = thresholds.length ? Math.min(...thresholds) : 5;
      const upper = thresholds.length > 1 ? Math.max(...thresholds) : 10;
      const value = sandboxNumber(values[0]);
      return { status: "ok", value: value >= lower && value <= upper };
    }
    if (op === "delay") {
      const delayed = state.previous_outputs[node.id] !== undefined
        ? state.previous_outputs[node.id]
        : false;
      return { status: "ok", value: delayed };
    }
    if (op === "latch") {
      const latched = sandboxBoolean(state.previous_outputs[node.id]) || sandboxBoolean(values[0]);
      return { status: "ok", value: latched };
    }
    return { status: "ok", value: values.every((value) => sandboxBoolean(value)) };
  }

  function evaluateSandboxTestBench(snapshot, definition) {
    const model = snapshot && typeof snapshot === "object" && !Array.isArray(snapshot)
      ? snapshot
      : currentDraftSnapshot();
    const testBench = definition || currentSandboxTestBenchDefinition();
    const nodesForRun = Array.isArray(model.nodes) ? model.nodes : [];
    const edgesForRun = Array.isArray(model.edges) ? model.edges : [];
    const validationFindings = [];
    const trace = [];
    const state = { previous_outputs: {} };
    for (const tick of testBench.ticks || []) {
      const values = { ...(tick.inputs || {}) };
      const nodeResults = [];
      for (let pass = 0; pass < Math.max(1, nodesForRun.length); pass += 1) {
        propagateSandboxEdges(values, edgesForRun);
        for (const node of nodesForRun) {
          const result = evaluateSandboxNode(
            node,
            nodeInputValues(node, values, edgesForRun),
            state,
          );
          if (result.finding) validationFindings.push(result.finding);
          writeSandboxNodeOutput(values, node, result.value);
          nodeResults.push({
            node_id: node.id,
            op: node.op || node.op_catalog_entry || "and",
            value: normalizeEvidenceArchiveValue(result.value),
            status: result.status,
            truth_effect: "none",
          });
        }
      }
      propagateSandboxEdges(values, edgesForRun);
      trace.push({
        tick: tick.tick,
        values: normalizeEvidenceArchiveValue(values),
        node_results: nodeResults,
        truth_effect: "none",
      });
      state.previous_outputs = { ...values };
    }
    const assertions = (testBench.assertions || []).map((assertion) => {
      const frame = trace.find((item) => Number(item.tick) === Number(assertion.tick));
      const observed = frame && frame.values
        ? readSandboxValue(frame.values, [assertion.target])
        : undefined;
      const status = sandboxValueEquals(observed, assertion.expected) ? "pass" : "fail";
      return {
        tick: assertion.tick,
        target: assertion.target,
        expected: assertion.expected,
        observed: normalizeEvidenceArchiveValue(observed),
        comparator: assertion.comparator || "equals",
        status,
        truth_effect: "none",
      };
    });
    const failCount = assertions.filter((assertion) => assertion.status === "fail").length;
    const unsupportedOps = validationFindings.filter((finding) => finding.code === "unsupported_op");
    const assertionStatus = assertions.length === 0
      ? "not_run"
      : (failCount ? "fail" : "pass");
    const status = unsupportedOps.length
      ? "invalid_scenario"
      : (failCount ? "fail" : "pass");
    return {
      kind: sandboxTestRunReportKind,
      version: sandboxTestRunReportVersion,
      scenario_id: testBench.scenario_id || selectedWorkbenchScenarioId(),
      model_hash: sandboxCandidateModelHash(nodesForRun, edgesForRun, testBench),
      definition: testBench,
      status,
      assertion_status: assertionStatus,
      pass_count: assertions.filter((assertion) => assertion.status === "pass").length,
      fail_count: failCount,
      assertion_count: assertions.length,
      trace,
      assertions,
      validation_findings: validationFindings,
      unsupported_ops: unsupportedOps,
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_level_impact: "none",
      truth_effect: "none",
    };
  }

  function renderSandboxTestBenchReport(report) {
    const normalized = normalizeImportedSandboxTestRunReport(report);
    lastSandboxTestRunReport = normalized;
    const status = (normalized && normalized.status) || "invalid_scenario";
    if (sandboxTestBenchPanel) sandboxTestBenchPanel.setAttribute("data-test-status", status);
    if (sandboxTestBenchStatus) sandboxTestBenchStatus.textContent = status;
    if (sandboxTestBenchReportOutput) {
      sandboxTestBenchReportOutput.value = JSON.stringify(normalized, null, 2);
    }
    if (handoffStatus) {
      handoffStatus.textContent =
        `Sandbox test bench ${status}. Truth effect: none. No certification claim.`;
    }
    renderCandidateDebuggerView(currentCandidateDebuggerView("test_bench"));
    lastPreflightAnalyzerReport = null;
    renderWorkbenchPreflightAnalyzerReport(currentPreflightAnalyzerReport("test_bench"));
    return normalized;
  }

  function runSandboxTestBench() {
    let report = null;
    if (runTestBenchBtn) runTestBenchBtn.disabled = true;
    if (sandboxTestBenchStatus) sandboxTestBenchStatus.textContent = "running";
    try {
      const definition = currentSandboxTestBenchDefinition();
      report = evaluateSandboxTestBench(currentDraftSnapshot(), definition);
    } catch (err) {
      report = {
        kind: sandboxTestRunReportKind,
        version: sandboxTestRunReportVersion,
        scenario_id: selectedWorkbenchScenarioId(),
        status: "invalid_scenario",
        assertion_status: "not_run",
        pass_count: 0,
        fail_count: 0,
        assertion_count: 0,
        error: err && err.message ? err.message : "sandbox test bench failed",
        definition: null,
        trace: [],
        assertions: [],
        validation_findings: [],
        unsupported_ops: [],
        candidate_state: "sandbox_candidate",
        certification_claim: "none",
        truth_level_impact: "none",
        truth_effect: "none",
      };
    } finally {
      if (runTestBenchBtn) runTestBenchBtn.disabled = false;
    }
    recordWorkspaceAction("run_sandbox_test_bench");
    recordCanvasInteractionAction("run_sandbox_test_bench");
    renderWorkspaceDocumentStatus();
    renderSandboxTestBenchReport(report);
    persistDraft();
    return report;
  }

  function buildEditableDraftExport() {
    const snapshot = currentDraftSnapshot();
    const customSnapshot = safeWorkbenchCustomSnapshot() || {};
    const changedModelHash = editableDraftHash(stableEvidenceArchiveJson(snapshot));
    const changeRequestProofPacket = buildChangeRequestProofPacket(snapshot, changedModelHash);
    const linearIssueBody = linearIssueBodyFromProofPacket(changeRequestProofPacket);
    const prProofPacket = prProofTextFromProofPacket(changeRequestProofPacket);
    const changeRequestHandoffPacket =
      buildChangeRequestHandoffPacket(changeRequestProofPacket, linearIssueBody, prProofPacket);
    const candidateBaselineDiffReviewV2 =
      currentCandidateBaselineDiffReviewV2Report("export", changedModelHash);
    return {
      kind: "well-harness-workbench-ui-draft",
      version: 1,
      draft_state: snapshot.draft_state,
      canvas_authoring_mode: snapshot.canvas_authoring_mode,
      system_id: snapshot.system_id,
      baseline_adapter: snapshot.baseline_adapter,
      truth_level_impact: "none",
      dal_pssa_impact: "none",
      controller_truth_modified: false,
      changed_model_hash: changedModelHash,
      workspace_document: snapshot.workspace_document,
      canvas_interaction_summary: snapshot.canvas_interaction_summary,
      editable_graph_document: snapshot.editable_graph_document,
      diagnostic_focus: snapshot.diagnostic_focus,
      viewport_state: snapshot.viewport_state,
      selected_node: snapshot.selected_node,
      selected_node_ids: snapshot.selected_node_ids,
      nodes: snapshot.nodes,
      ports: snapshot.ports,
      typed_ports: snapshot.typed_ports,
      edges: snapshot.edges,
      hardware_bindings: snapshot.hardware_bindings,
      binding_coverage: snapshot.binding_coverage,
      hardware_binding_diagnostics: snapshot.hardware_binding_diagnostics,
      interface_matrix: snapshot.interface_matrix,
      interface_matrix_validation: snapshot.interface_matrix_validation,
      connector_pin_map: snapshot.connector_pin_map,
      repair_action_log: snapshot.repair_action_log,
      port_contract_summary: snapshot.port_contract_summary,
      port_compatibility_report: snapshot.port_compatibility_report,
      operation_catalog: snapshot.operation_catalog,
      component_library: snapshot.component_library,
      subsystem_groups: snapshot.subsystem_groups,
      subsystem_interface_contracts: snapshot.subsystem_interface_contracts,
      rule_parameter_summary: snapshot.rule_parameter_summary,
      hardware_palette: snapshot.hardware_palette,
      hardware_evidence_v2: snapshot.hardware_evidence_v2,
      selected_debug_timeline: snapshot.selected_debug_timeline,
      candidate_baseline_diff_review_v2: candidateBaselineDiffReviewV2,
      sandbox_test_bench: snapshot.sandbox_test_bench,
      sandbox_test_run_report: snapshot.sandbox_test_run_report,
      candidate_debugger_view: snapshot.candidate_debugger_view,
      preflight_analyzer_report: snapshot.preflight_analyzer_report,
      hardware_interface_designer: snapshot.hardware_interface_designer,
      hardware_interface_designer_validation: snapshot.hardware_interface_designer_validation,
      changerequest_proof_packet: changeRequestProofPacket,
      changerequest_handoff_packet: changeRequestHandoffPacket,
      draft_snapshot_manifest: buildDraftSnapshotManifestSummary(),
      selected_scenario_id: selectedWorkbenchScenarioId(),
      custom_snapshot: customSnapshot,
      source_refs: uniqueSourceRefs(),
      latest_sandbox_verdict: (lastSandboxDiff && lastSandboxDiff.verdict) || "not_run",
    };
  }

  function graphDocumentDraftState(payload) {
    if (!payload || typeof payload !== "object" || Array.isArray(payload)) return payload;
    const graphDocument =
      payload.editable_graph_document
      && typeof payload.editable_graph_document === "object"
      && !Array.isArray(payload.editable_graph_document)
        ? payload.editable_graph_document
        : null;
    const canonicalModel =
      graphDocument
      && graphDocument.canonical_model
      && typeof graphDocument.canonical_model === "object"
      && !Array.isArray(graphDocument.canonical_model)
        ? graphDocument.canonical_model
        : null;
    if (!canonicalModel) return payload;
    const nextPayload = { ...payload };
    for (const key of ["nodes", "edges", "ports", "typed_ports", "subsystem_groups", "hardware_bindings"]) {
      if (!Array.isArray(nextPayload[key]) && Array.isArray(canonicalModel[key])) {
        nextPayload[key] = canonicalModel[key];
      }
    }
    if (
      nextPayload.component_library === undefined
      && canonicalModel.component_library
      && typeof canonicalModel.component_library === "object"
      && !Array.isArray(canonicalModel.component_library)
    ) {
      nextPayload.component_library = canonicalModel.component_library;
    }
    if (
      nextPayload.sandbox_test_bench === undefined
      && canonicalModel.sandbox_test_bench
      && typeof canonicalModel.sandbox_test_bench === "object"
      && !Array.isArray(canonicalModel.sandbox_test_bench)
    ) {
      nextPayload.sandbox_test_bench = canonicalModel.sandbox_test_bench;
    }
    if (
      nextPayload.hardware_interface_designer === undefined
      && canonicalModel.hardware_interface_designer
      && typeof canonicalModel.hardware_interface_designer === "object"
      && !Array.isArray(canonicalModel.hardware_interface_designer)
    ) {
      nextPayload.hardware_interface_designer = canonicalModel.hardware_interface_designer;
    }
    if (
      nextPayload.viewport_state === undefined
      && canonicalModel.viewport_state
      && typeof canonicalModel.viewport_state === "object"
      && !Array.isArray(canonicalModel.viewport_state)
    ) {
      nextPayload.viewport_state = canonicalModel.viewport_state;
    }
    if (nextPayload.canvas_authoring_mode === undefined && canonicalModel.canvas_authoring_mode) {
      nextPayload.canvas_authoring_mode = canonicalModel.canvas_authoring_mode;
    }
    if (!Array.isArray(nextPayload.selected_node_ids) && Array.isArray(canonicalModel.selected_node_ids)) {
      nextPayload.selected_node_ids = canonicalModel.selected_node_ids;
    }
    return nextPayload;
  }

  function validateEditableDraftImport(payload) {
    if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
      throw new Error("draft JSON must be an object");
    }
    payload = graphDocumentDraftState(payload);
    if (payload.kind !== "well-harness-workbench-ui-draft") {
      throw new Error("kind must be well-harness-workbench-ui-draft");
    }
    if (payload.version !== 1) {
      throw new Error("version must be 1");
    }
    if (payload.system_id !== "thrust-reverser") {
      throw new Error("system_id must be thrust-reverser");
    }
    if (payload.truth_level_impact !== "none") {
      throw new Error("truth_level_impact must be none");
    }
    if (payload.dal_pssa_impact !== "none") {
      throw new Error("dal_pssa_impact must be none");
    }
    if (payload.controller_truth_modified !== false) {
      throw new Error("controller_truth_modified must be false");
    }
    if (
      payload.canvas_authoring_mode !== undefined
      && !["reference_sample", "empty_authoring"].includes(payload.canvas_authoring_mode)
    ) {
      throw new Error("canvas_authoring_mode must be reference_sample or empty_authoring");
    }
    if (
      payload.workspace_document !== undefined
      && (!payload.workspace_document || typeof payload.workspace_document !== "object" || Array.isArray(payload.workspace_document))
    ) {
      throw new Error("workspace_document must be an object when present");
    }
    if (payload.workspace_document !== undefined) {
      const documentRecord = payload.workspace_document;
      if (documentRecord.kind !== workspaceDocumentKind) {
        throw new Error("workspace_document kind must be well-harness-workbench-workspace-document");
      }
      if (documentRecord.version !== workspaceDocumentVersion) {
        throw new Error("workspace_document version must be workbench-workspace-document.v1");
      }
      if (documentRecord.candidate_state !== "sandbox_candidate") {
        throw new Error("workspace_document candidate_state must be sandbox_candidate");
      }
      if (documentRecord.truth_effect !== "none") {
        throw new Error("workspace_document truth_effect must be none");
      }
      for (const key of ["document_id", "revision_id", "action_log_digest"]) {
        if (typeof documentRecord[key] !== "string" || !documentRecord[key]) {
          throw new Error(`workspace_document ${key} must be a non-empty string`);
        }
      }
      for (const key of ["action_count", "undo_depth", "redo_depth"]) {
        if (!Number.isFinite(Number(documentRecord[key]))) {
          throw new Error(`workspace_document ${key} must be numeric`);
        }
      }
      if (documentRecord.action_log !== undefined && !Array.isArray(documentRecord.action_log)) {
        throw new Error("workspace_document action_log must be an array when present");
      }
    }
    if (
      payload.canvas_interaction_summary !== undefined
      && (!payload.canvas_interaction_summary || typeof payload.canvas_interaction_summary !== "object" || Array.isArray(payload.canvas_interaction_summary))
    ) {
      throw new Error("canvas_interaction_summary must be an object when present");
    }
    if (payload.canvas_interaction_summary !== undefined) {
      const summary = payload.canvas_interaction_summary;
      if (summary.kind !== canvasInteractionSummaryKind) {
        throw new Error("canvas_interaction_summary kind must be well-harness-workbench-canvas-interaction-summary");
      }
      if (summary.version !== canvasInteractionSummaryVersion) {
        throw new Error("canvas_interaction_summary version must be workbench-canvas-interaction-summary.v1");
      }
      if (summary.candidate_state !== "sandbox_candidate") {
        throw new Error("canvas_interaction_summary candidate_state must be sandbox_candidate");
      }
      if (summary.truth_effect !== "none") {
        throw new Error("canvas_interaction_summary truth_effect must be none");
      }
      for (const key of ["selected_node_count", "selected_edge_count", "node_count", "edge_count"]) {
        if (!Number.isFinite(Number(summary[key]))) {
          throw new Error(`canvas_interaction_summary ${key} must be numeric`);
        }
      }
    }
    if (
      payload.editable_graph_document !== undefined
      && (
        !payload.editable_graph_document
        || typeof payload.editable_graph_document !== "object"
        || Array.isArray(payload.editable_graph_document)
      )
    ) {
      throw new Error("editable_graph_document must be an object when present");
    }
    if (payload.editable_graph_document !== undefined) {
      const graphDocument = payload.editable_graph_document;
      if (graphDocument.kind !== editableGraphDocumentKind) {
        throw new Error("editable_graph_document kind must be well-harness-workbench-editable-graph-document");
      }
      if (!editableGraphDocumentAcceptedImportVersions.includes(graphDocument.version)) {
        throw new Error("editable_graph_document version must be workbench-editable-graph-document.v1 or workbench-editable-graph-document.v2");
      }
      if (graphDocument.candidate_state !== "sandbox_candidate") {
        throw new Error("editable_graph_document candidate_state must be sandbox_candidate");
      }
      if (graphDocument.truth_effect !== "none") {
        throw new Error("editable_graph_document truth_effect must be none");
      }
      if (graphDocument.version === editableGraphDocumentVersion) {
        const canonicalModel = graphDocument.canonical_model;
        if (!canonicalModel || typeof canonicalModel !== "object" || Array.isArray(canonicalModel)) {
          throw new Error("editable_graph_document canonical_model must be an object");
        }
        if (canonicalModel.schema_version !== editableGraphCanonicalModelVersion) {
          throw new Error("editable_graph_document canonical_model schema_version must be workbench-editable-graph-canonical-model.v1");
        }
        if (canonicalModel.candidate_state !== "sandbox_candidate") {
          throw new Error("editable_graph_document canonical_model candidate_state must be sandbox_candidate");
        }
        if (canonicalModel.truth_effect !== "none") {
          throw new Error("editable_graph_document canonical_model truth_effect must be none");
        }
        for (const key of ["nodes", "edges", "ports", "typed_ports", "subsystem_groups"]) {
          if (!Array.isArray(canonicalModel[key])) {
            throw new Error(`editable_graph_document canonical_model ${key} must be an array`);
          }
        }
        const domAdapter = graphDocument.dom_adapter;
        if (!domAdapter || typeof domAdapter !== "object" || Array.isArray(domAdapter)) {
          throw new Error("editable_graph_document dom_adapter must be an object");
        }
        if (domAdapter.kind !== "workbench-editable-graph-dom-adapter-boundary") {
          throw new Error("editable_graph_document dom_adapter kind must be workbench-editable-graph-dom-adapter-boundary");
        }
        if (domAdapter.version !== editableGraphDomAdapterBoundaryVersion) {
          throw new Error("editable_graph_document dom_adapter version must be workbench-editable-graph-dom-adapter-boundary.v1");
        }
        if (domAdapter.source_of_truth !== "editable_graph_document.canonical_model") {
          throw new Error("editable_graph_document dom_adapter source_of_truth must be canonical_model");
        }
        if (domAdapter.top_level_compatibility !== true) {
          throw new Error("editable_graph_document dom_adapter top_level_compatibility must be true");
        }
        if (domAdapter.truth_effect !== "none") {
          throw new Error("editable_graph_document dom_adapter truth_effect must be none");
        }
      }
      for (const key of ["document_id", "workspace_revision_id", "action_log_digest"]) {
        if (typeof graphDocument[key] !== "string" || !graphDocument[key]) {
          throw new Error(`editable_graph_document ${key} must be a non-empty string`);
        }
      }
      for (const key of [
        "node_count",
        "draft_node_count",
        "edge_count",
        "port_count",
        "typed_port_count",
        "subsystem_group_count",
        "component_template_count",
        "selected_node_count",
        "selected_edge_count",
      ]) {
        if (!Number.isFinite(Number(graphDocument[key]))) {
          throw new Error(`editable_graph_document ${key} must be numeric`);
        }
      }
      for (const key of ["node_ids", "edge_ids", "port_ids", "subsystem_group_ids"]) {
        if (!Array.isArray(graphDocument[key])) {
          throw new Error(`editable_graph_document ${key} must be an array`);
        }
      }
      if (
        !graphDocument.selected_state
        || typeof graphDocument.selected_state !== "object"
        || Array.isArray(graphDocument.selected_state)
      ) {
        throw new Error("editable_graph_document selected_state must be an object");
      }
    }
    if (!Array.isArray(payload.nodes)) {
      throw new Error("nodes must be an array");
    }
    if (payload.edges !== undefined && !Array.isArray(payload.edges)) {
      throw new Error("edges must be an array when present");
    }
    if (payload.editable_graph_document !== undefined) {
      const graphDocument = payload.editable_graph_document;
      const ports = Array.isArray(payload.ports) ? payload.ports : [];
      const typedPorts = Array.isArray(payload.typed_ports) ? payload.typed_ports : [];
      const subsystemGroups = Array.isArray(payload.subsystem_groups) ? payload.subsystem_groups : [];
      const componentLibrary =
        payload.component_library && typeof payload.component_library === "object" && !Array.isArray(payload.component_library)
          ? payload.component_library
          : {};
      const capturedTemplates = Array.isArray(componentLibrary.captured_templates)
        ? componentLibrary.captured_templates
        : [];
      const graphCountExpectations = {
        node_count: payload.nodes.length,
        draft_node_count: payload.nodes.filter((node) => Boolean(node && (node.draftNode || node.draft_node))).length,
        edge_count: Array.isArray(payload.edges) ? payload.edges.length : 0,
        port_count: ports.length,
        typed_port_count: typedPorts.length,
        subsystem_group_count: subsystemGroups.length,
        component_template_count: capturedTemplates.length,
      };
      for (const [key, expected] of Object.entries(graphCountExpectations)) {
        if (Number(graphDocument[key]) !== expected) {
          throw new Error(`editable_graph_document ${key} must match draft payload`);
        }
      }
    }
    if (payload.hardware_bindings !== undefined && !Array.isArray(payload.hardware_bindings)) {
      throw new Error("hardware_bindings must be an array when present");
    }
    if (
      payload.hardware_binding_diagnostics !== undefined
      && (!payload.hardware_binding_diagnostics || typeof payload.hardware_binding_diagnostics !== "object" || Array.isArray(payload.hardware_binding_diagnostics))
    ) {
      throw new Error("hardware_binding_diagnostics must be an object when present");
    }
    if (
      payload.interface_matrix !== undefined
      && (!payload.interface_matrix || typeof payload.interface_matrix !== "object" || Array.isArray(payload.interface_matrix))
    ) {
      throw new Error("interface_matrix must be an object when present");
    }
    if (
      payload.interface_matrix !== undefined
      && payload.interface_matrix.truth_effect !== "none"
    ) {
      throw new Error("interface_matrix truth_effect must be none");
    }
    if (
      payload.interface_matrix_validation !== undefined
      && payload.interface_matrix_validation !== null
      && (!payload.interface_matrix_validation || typeof payload.interface_matrix_validation !== "object" || Array.isArray(payload.interface_matrix_validation))
    ) {
      throw new Error("interface_matrix_validation must be an object when present");
    }
    if (
      payload.interface_matrix_validation
      && payload.interface_matrix_validation.truth_effect !== "none"
    ) {
      throw new Error("interface_matrix_validation truth_effect must be none");
    }
    if (
      payload.connector_pin_map !== undefined
      && (!payload.connector_pin_map || typeof payload.connector_pin_map !== "object" || Array.isArray(payload.connector_pin_map))
    ) {
      throw new Error("connector_pin_map must be an object when present");
    }
    if (
      payload.connector_pin_map !== undefined
      && payload.connector_pin_map.truth_effect !== "none"
    ) {
      throw new Error("connector_pin_map truth_effect must be none");
    }
    if (
      payload.hardware_interface_designer !== undefined
      && (!payload.hardware_interface_designer || typeof payload.hardware_interface_designer !== "object" || Array.isArray(payload.hardware_interface_designer))
    ) {
      throw new Error("hardware_interface_designer must be an object when present");
    }
    if (payload.hardware_interface_designer !== undefined) {
      const designer = normalizeHardwareInterfaceDesignerPayload(payload.hardware_interface_designer);
      const report = buildHardwareInterfaceDesignerValidationReport(designer);
      if (designer.kind !== hardwareInterfaceDesignerKind) {
        throw new Error("hardware_interface_designer kind must be well-harness-editable-hardware-interface-design");
      }
      if (designer.$schema !== hardwareInterfaceDesignerSchemaId) {
        throw new Error("hardware_interface_designer schema must be editable_hardware_interface_design_v1.schema.json");
      }
      if (designer.runtime_truth_effect !== "none") {
        throw new Error("hardware_interface_designer truth_effect must be none");
      }
      if (report.status === "fail") {
        throw new Error("hardware_interface_designer validation must pass before import");
      }
    }
    if (
      payload.hardware_interface_designer_validation !== undefined
      && payload.hardware_interface_designer_validation !== null
      && (!payload.hardware_interface_designer_validation || typeof payload.hardware_interface_designer_validation !== "object" || Array.isArray(payload.hardware_interface_designer_validation))
    ) {
      throw new Error("hardware_interface_designer_validation must be an object when present");
    }
    if (payload.hardware_interface_designer_validation) {
      const report = payload.hardware_interface_designer_validation;
      if (report.kind !== hardwareInterfaceDesignerValidationKind) {
        throw new Error("hardware_interface_designer_validation kind must be well-harness-workbench-hardware-interface-designer-validation-report");
      }
      if (report.version !== hardwareInterfaceDesignerValidationVersion) {
        throw new Error("hardware_interface_designer_validation version must be workbench-hardware-interface-designer-validation.v1");
      }
      if (!["pass", "warn", "fail"].includes(report.status)) {
        throw new Error("hardware_interface_designer_validation status must be pass, warn, or fail");
      }
      if (report.candidate_state !== "sandbox_candidate") {
        throw new Error("hardware_interface_designer_validation candidate_state must be sandbox_candidate");
      }
      if (report.certification_claim !== "none") {
        throw new Error("hardware_interface_designer_validation certification_claim must be none");
      }
      if (report.truth_effect !== "none") {
        throw new Error("hardware_interface_designer_validation truth_effect must be none");
      }
    }
    if (
      payload.hardware_evidence_v2 !== undefined
      && (!payload.hardware_evidence_v2 || typeof payload.hardware_evidence_v2 !== "object" || Array.isArray(payload.hardware_evidence_v2))
    ) {
      throw new Error("hardware_evidence_v2 must be an object when present");
    }
    if (
      payload.hardware_evidence_v2 !== undefined
      && payload.hardware_evidence_v2.truth_effect !== "none"
    ) {
      throw new Error("hardware_evidence_v2 truth_effect must be none");
    }
    if (
      payload.selected_debug_timeline !== undefined
      && (!payload.selected_debug_timeline || typeof payload.selected_debug_timeline !== "object" || Array.isArray(payload.selected_debug_timeline))
    ) {
      throw new Error("selected_debug_timeline must be an object when present");
    }
    if (
      payload.selected_debug_timeline !== undefined
      && payload.selected_debug_timeline.truth_effect !== "none"
    ) {
      throw new Error("selected_debug_timeline truth_effect must be none");
    }
    if (
      payload.candidate_baseline_diff_review_v2 !== undefined
      && (!payload.candidate_baseline_diff_review_v2 || typeof payload.candidate_baseline_diff_review_v2 !== "object" || Array.isArray(payload.candidate_baseline_diff_review_v2))
    ) {
      throw new Error("candidate_baseline_diff_review_v2 must be an object when present");
    }
    if (payload.candidate_baseline_diff_review_v2 !== undefined) {
      const review = payload.candidate_baseline_diff_review_v2;
      if (review.candidate_state !== "sandbox_candidate") {
        throw new Error("candidate_baseline_diff_review_v2 candidate_state must be sandbox_candidate");
      }
      if (review.certification_claim !== "none") {
        throw new Error("candidate_baseline_diff_review_v2 certification_claim must be none");
      }
      if (review.truth_effect !== "none") {
        throw new Error("candidate_baseline_diff_review_v2 truth_effect must be none");
      }
      if (review.controller_truth_modified !== false) {
        throw new Error("candidate_baseline_diff_review_v2 controller_truth_modified must be false");
      }
    }
    if (
      payload.sandbox_test_bench !== undefined
      && payload.sandbox_test_bench !== null
      && (!payload.sandbox_test_bench || typeof payload.sandbox_test_bench !== "object" || Array.isArray(payload.sandbox_test_bench))
    ) {
      throw new Error("sandbox_test_bench must be an object when present");
    }
    if (payload.sandbox_test_bench) {
      const testBench = payload.sandbox_test_bench;
      if (testBench.kind !== sandboxTestBenchKind) {
        throw new Error("sandbox_test_bench kind must be well-harness-workbench-sandbox-test-bench");
      }
      if (testBench.version !== sandboxTestBenchVersion) {
        throw new Error("sandbox_test_bench version must be workbench-sandbox-test-bench.v1");
      }
      if (testBench.candidate_state !== "sandbox_candidate") {
        throw new Error("sandbox_test_bench candidate_state must be sandbox_candidate");
      }
      if (testBench.certification_claim !== "none") {
        throw new Error("sandbox_test_bench certification_claim must be none");
      }
      if (testBench.truth_effect !== "none") {
        throw new Error("sandbox_test_bench truth_effect must be none");
      }
      if (!Array.isArray(testBench.ticks)) {
        throw new Error("sandbox_test_bench ticks must be an array");
      }
      if (!Array.isArray(testBench.assertions)) {
        throw new Error("sandbox_test_bench assertions must be an array");
      }
    }
    if (
      payload.sandbox_test_run_report !== undefined
      && payload.sandbox_test_run_report !== null
      && (!payload.sandbox_test_run_report || typeof payload.sandbox_test_run_report !== "object" || Array.isArray(payload.sandbox_test_run_report))
    ) {
      throw new Error("sandbox_test_run_report must be an object when present");
    }
    if (payload.sandbox_test_run_report) {
      const report = payload.sandbox_test_run_report;
      if (report.kind !== sandboxTestRunReportKind) {
        throw new Error("sandbox_test_run_report kind must be well-harness-workbench-sandbox-test-run-report");
      }
      if (report.version !== sandboxTestRunReportVersion) {
        throw new Error("sandbox_test_run_report version must be workbench-sandbox-test-run-report.v1");
      }
      if (report.candidate_state !== "sandbox_candidate") {
        throw new Error("sandbox_test_run_report candidate_state must be sandbox_candidate");
      }
      if (report.certification_claim !== "none") {
        throw new Error("sandbox_test_run_report certification_claim must be none");
      }
      if (report.truth_effect !== "none") {
        throw new Error("sandbox_test_run_report truth_effect must be none");
      }
    }
    if (
      payload.candidate_debugger_view !== undefined
      && payload.candidate_debugger_view !== null
      && (!payload.candidate_debugger_view || typeof payload.candidate_debugger_view !== "object" || Array.isArray(payload.candidate_debugger_view))
    ) {
      throw new Error("candidate_debugger_view must be an object when present");
    }
    if (payload.candidate_debugger_view) {
      const debuggerView = payload.candidate_debugger_view;
      if (debuggerView.kind !== candidateDebuggerViewKind) {
        throw new Error("candidate_debugger_view kind must be well-harness-workbench-candidate-debugger-view");
      }
      if (debuggerView.version !== candidateDebuggerViewVersion) {
        throw new Error("candidate_debugger_view version must be workbench-candidate-debugger-view.v1");
      }
      if (debuggerView.candidate_state !== "sandbox_candidate") {
        throw new Error("candidate_debugger_view candidate_state must be sandbox_candidate");
      }
      if (debuggerView.certification_claim !== "none") {
        throw new Error("candidate_debugger_view certification_claim must be none");
      }
      if (debuggerView.truth_effect !== "none") {
        throw new Error("candidate_debugger_view truth_effect must be none");
      }
    }
    if (
      payload.preflight_analyzer_report !== undefined
      && payload.preflight_analyzer_report !== null
      && (!payload.preflight_analyzer_report || typeof payload.preflight_analyzer_report !== "object" || Array.isArray(payload.preflight_analyzer_report))
    ) {
      throw new Error("preflight_analyzer_report must be an object when present");
    }
    if (payload.preflight_analyzer_report) {
      const report = payload.preflight_analyzer_report;
      if (report.kind !== preflightAnalyzerReportKind) {
        throw new Error("preflight_analyzer_report kind must be well-harness-workbench-preflight-analyzer-report");
      }
      if (report.version !== preflightAnalyzerReportVersion) {
        throw new Error("preflight_analyzer_report version must be workbench-preflight-analyzer.v1");
      }
      if (!["ready", "needs_evidence", "invalid_candidate"].includes(report.classification)) {
        throw new Error("preflight_analyzer_report classification must be ready, needs_evidence, or invalid_candidate");
      }
      if (report.candidate_state !== "sandbox_candidate") {
        throw new Error("preflight_analyzer_report candidate_state must be sandbox_candidate");
      }
      if (report.certification_claim !== "none") {
        throw new Error("preflight_analyzer_report certification_claim must be none");
      }
      if (report.truth_effect !== "none") {
        throw new Error("preflight_analyzer_report truth_effect must be none");
      }
    }
    if (payload.typed_ports !== undefined && !Array.isArray(payload.typed_ports)) {
      throw new Error("typed_ports must be an array when present");
    }
    if (
      payload.port_contract_summary !== undefined
      && (!payload.port_contract_summary || typeof payload.port_contract_summary !== "object" || Array.isArray(payload.port_contract_summary))
    ) {
      throw new Error("port_contract_summary must be an object when present");
    }
    if (
      payload.port_compatibility_report !== undefined
      && (!payload.port_compatibility_report || typeof payload.port_compatibility_report !== "object" || Array.isArray(payload.port_compatibility_report))
    ) {
      throw new Error("port_compatibility_report must be an object when present");
    }
    if (
      payload.operation_catalog !== undefined
      && (!payload.operation_catalog || typeof payload.operation_catalog !== "object" || Array.isArray(payload.operation_catalog))
    ) {
      throw new Error("operation_catalog must be an object when present");
    }
    if (
      payload.component_library !== undefined
      && (!payload.component_library || typeof payload.component_library !== "object" || Array.isArray(payload.component_library))
    ) {
      throw new Error("component_library must be an object when present");
    }
    if (payload.component_library && payload.component_library.truth_effect !== "none") {
      throw new Error("component_library truth_effect must be none");
    }
    if (payload.component_library && payload.component_library.captured_templates !== undefined) {
      if (!Array.isArray(payload.component_library.captured_templates)) {
        throw new Error("component_library captured_templates must be an array");
      }
      for (const template of payload.component_library.captured_templates) {
        if (!template || typeof template !== "object" || Array.isArray(template)) {
          throw new Error("component_library captured_templates entries must be objects");
        }
        if (template.candidate_state !== "sandbox_candidate") {
          throw new Error("captured subsystem template candidate_state must be sandbox_candidate");
        }
        if (template.truth_effect !== "none") {
          throw new Error("captured subsystem template truth_effect must be none");
        }
      }
    }
    if (payload.component_library && payload.component_library.captured_subsystem_templates !== undefined) {
      if (!Array.isArray(payload.component_library.captured_subsystem_templates)) {
        throw new Error("component_library captured_subsystem_templates must be an array");
      }
    }
    if (payload.subsystem_groups !== undefined && !Array.isArray(payload.subsystem_groups)) {
      throw new Error("subsystem_groups must be an array when present");
    }
    if (Array.isArray(payload.subsystem_groups)) {
      for (const group of payload.subsystem_groups) {
        if (!group || typeof group !== "object" || Array.isArray(group)) {
          throw new Error("subsystem_groups entries must be objects");
        }
        if (!Array.isArray(group.node_ids)) {
          throw new Error("subsystem_groups node_ids must be arrays");
        }
        if (group.truth_effect !== undefined && group.truth_effect !== "none") {
          throw new Error("subsystem_groups truth_effect must be none");
        }
        if (group.interface_contracts !== undefined && !Array.isArray(group.interface_contracts)) {
          throw new Error("subsystem_groups interface_contracts must be arrays");
        }
        for (const port of Array.isArray(group.interface_contracts) ? group.interface_contracts : []) {
          if (!port || typeof port !== "object" || Array.isArray(port)) {
            throw new Error("subsystem interface contract entries must be objects");
          }
          if (port.candidate_state !== undefined && port.candidate_state !== "sandbox_candidate") {
            throw new Error("subsystem interface contract candidate_state must be sandbox_candidate");
          }
          if (port.truth_effect !== undefined && port.truth_effect !== "none") {
            throw new Error("subsystem interface contract truth_effect must be none");
          }
        }
      }
    }
    if (
      payload.subsystem_interface_contracts !== undefined
      && (!payload.subsystem_interface_contracts || typeof payload.subsystem_interface_contracts !== "object" || Array.isArray(payload.subsystem_interface_contracts))
    ) {
      throw new Error("subsystem_interface_contracts must be an object when present");
    }
    if (payload.subsystem_interface_contracts !== undefined) {
      const contracts = payload.subsystem_interface_contracts;
      if (contracts.candidate_state !== "sandbox_candidate") {
        throw new Error("subsystem_interface_contracts candidate_state must be sandbox_candidate");
      }
      if (contracts.truth_effect !== "none") {
        throw new Error("subsystem interface contracts truth_effect must be none");
      }
      if (!Array.isArray(contracts.groups)) {
        throw new Error("subsystem_interface_contracts groups must be an array");
      }
    }
    if (
      payload.rule_parameter_summary !== undefined
      && (!payload.rule_parameter_summary || typeof payload.rule_parameter_summary !== "object" || Array.isArray(payload.rule_parameter_summary))
    ) {
      throw new Error("rule_parameter_summary must be an object when present");
    }
    if (
      payload.custom_snapshot !== undefined
      && (!payload.custom_snapshot || typeof payload.custom_snapshot !== "object" || Array.isArray(payload.custom_snapshot))
    ) {
      throw new Error("custom_snapshot must be an object when present");
    }
    if (
      payload.viewport_state !== undefined
      && (!payload.viewport_state || typeof payload.viewport_state !== "object" || Array.isArray(payload.viewport_state))
    ) {
      throw new Error("viewport_state must be an object when present");
    }
    if (
      payload.diagnostic_focus !== undefined
      && (!payload.diagnostic_focus || typeof payload.diagnostic_focus !== "object" || Array.isArray(payload.diagnostic_focus))
    ) {
      throw new Error("diagnostic_focus must be an object when present");
    }
    if (payload.repair_action_log !== undefined && !Array.isArray(payload.repair_action_log)) {
      throw new Error("repair_action_log must be an array when present");
    }
    if (
      payload.changerequest_proof_packet !== undefined
      && (!payload.changerequest_proof_packet || typeof payload.changerequest_proof_packet !== "object" || Array.isArray(payload.changerequest_proof_packet))
    ) {
      throw new Error("changerequest_proof_packet must be an object when present");
    }
    if (payload.changerequest_proof_packet !== undefined) {
      const packet = payload.changerequest_proof_packet;
      if (packet.candidate_state !== "sandbox_candidate") {
        throw new Error("changerequest_proof_packet candidate_state must be sandbox_candidate");
      }
      if (packet.certification_claim !== "none") {
        throw new Error("changerequest_proof_packet certification_claim must be none");
      }
      if (packet.truth_effect !== "none") {
        throw new Error("changerequest_proof_packet truth_effect must be none");
      }
      if (packet.controller_truth_modified !== false) {
        throw new Error("changerequest_proof_packet controller_truth_modified must be false");
      }
    }
    if (
      payload.changerequest_handoff_packet !== undefined
      && (!payload.changerequest_handoff_packet || typeof payload.changerequest_handoff_packet !== "object" || Array.isArray(payload.changerequest_handoff_packet))
    ) {
      throw new Error("changerequest_handoff_packet must be an object when present");
    }
    if (payload.changerequest_handoff_packet !== undefined) {
      const packet = payload.changerequest_handoff_packet;
      if (packet.$schema !== "https://well-harness.local/json_schema/workbench_changerequest_handoff_v1.schema.json") {
        throw new Error("changerequest_handoff_packet schema must be workbench_changerequest_handoff_v1");
      }
      if (packet.candidate_state !== "sandbox_candidate") {
        throw new Error("changerequest_handoff_packet candidate_state must be sandbox_candidate");
      }
      if (packet.certification_claim !== "none") {
        throw new Error("changerequest_handoff_packet certification_claim must be none");
      }
      if (packet.truth_effect !== "none") {
        throw new Error("changerequest_handoff_packet truth_effect must be none");
      }
      if (packet.live_linear_mutation !== false) {
        throw new Error("changerequest_handoff_packet live_linear_mutation must be false");
      }
      if (packet.controller_truth_modified !== false) {
        throw new Error("changerequest_handoff_packet controller_truth_modified must be false");
      }
      if (packet.runtime_mutates_truth !== false) {
        throw new Error("changerequest_handoff_packet runtime_mutates_truth must be false");
      }
      if (!packet.serialization || packet.serialization.canonicalization !== "json.sort_keys.separators.v1") {
        throw new Error("changerequest_handoff_packet canonicalization must be stable JSON v1");
      }
    }
    return payload;
  }

  function updateNodeDisplay(node) {
    if (!node) return;
    const small = node.querySelector("small");
    if (small) {
      const op = node.getAttribute("data-node-op") || "and";
      const ruleCount = node.getAttribute("data-rule-count") || "0";
      small.textContent = `${op.toUpperCase()} · ${ruleCount} rules`;
    }
  }

  function applyEditableDraftImport(payload) {
    const validated = validateEditableDraftImport(payload);
    if (scenarioSelect && validated.selected_scenario_id) {
      scenarioSelect.value = String(validated.selected_scenario_id);
    }
    if (customSnapshotInput && validated.custom_snapshot) {
      customSnapshotInput.value = JSON.stringify(validated.custom_snapshot, null, 2);
    }
    restoreSandboxTestBenchDefinition(validated.sandbox_test_bench);
    lastSandboxTestRunReport = normalizeImportedSandboxTestRunReport(validated.sandbox_test_run_report);
    if (lastSandboxTestRunReport) {
      renderSandboxTestBenchReport(lastSandboxTestRunReport);
    }
    lastPreflightAnalyzerReport = normalizeImportedPreflightAnalyzerReport(validated.preflight_analyzer_report);
    if (lastPreflightAnalyzerReport) {
      renderWorkbenchPreflightAnalyzerReport(lastPreflightAnalyzerReport);
    }
    const selectedId =
      validated.selected_node && typeof validated.selected_node.id === "string"
        ? validated.selected_node.id
        : "";
    recordEditableHistory("import_draft");
    const importedCatalog = validated.operation_catalog || {};
    const importedComponentLibrary = validated.component_library || {};
    lastComponentTemplateId = String(importedComponentLibrary.last_template_id || "");
    capturedSubsystemTemplates = normalizeCapturedSubsystemTemplates(
      importedComponentLibrary.captured_templates
        || importedComponentLibrary.captured_subsystem_templates
        || [],
    );
    refreshCapturedSubsystemTemplateControls();
    lastInterfaceMatrixValidationReport = validated.interface_matrix_validation || null;
    if (interfaceMatrixValidationOutput) {
      interfaceMatrixValidationOutput.value = lastInterfaceMatrixValidationReport
        ? JSON.stringify(lastInterfaceMatrixValidationReport, null, 2)
        : "";
    }
    if (connectorPinMapOutput && validated.connector_pin_map) {
      connectorPinMapOutput.value = JSON.stringify(validated.connector_pin_map, null, 2);
    }
    lastHardwareInterfaceDesignerPayload =
      normalizeImportedHardwareInterfaceDesignerPayload(validated.hardware_interface_designer);
    lastHardwareInterfaceDesignerValidationReport =
      normalizeImportedHardwareInterfaceDesignerValidation(validated.hardware_interface_designer_validation)
      || (
        lastHardwareInterfaceDesignerPayload
          ? buildHardwareInterfaceDesignerValidationReport(lastHardwareInterfaceDesignerPayload)
          : null
      );
    if (lastHardwareInterfaceDesignerPayload && hardwareInterfaceDesignOutput) {
      hardwareInterfaceDesignOutput.value = JSON.stringify(lastHardwareInterfaceDesignerPayload, null, 2);
    }
    if (lastHardwareInterfaceDesignerValidationReport) {
      renderHardwareInterfaceDesignerValidationReport(lastHardwareInterfaceDesignerValidationReport);
    }
    applyEditableState({
      draftState: "derived",
      canvasAuthoringMode: validated.canvas_authoring_mode || "reference_sample",
      selectedNodeId: selectedId,
      selectedNodeIds: Array.isArray(validated.selected_node_ids)
        ? validated.selected_node_ids
        : [],
      diagnosticFocus: validated.diagnostic_focus || null,
      repairActionLog: validated.repair_action_log || [],
      viewportState: validated.viewport_state || defaultViewportState(),
      workspaceDocument: validated.workspace_document || null,
      canvasInteractionSummary: validated.canvas_interaction_summary || null,
      preflightAnalyzerReport: validated.preflight_analyzer_report || null,
      hardwareInterfaceDesigner: validated.hardware_interface_designer || null,
      hardwareInterfaceDesignerValidation: validated.hardware_interface_designer_validation || null,
      selectedCatalogOp: importedCatalog.selected_op,
      subsystemGroups: validated.subsystem_groups || [],
      nodes: validated.nodes.map((node) => ({
        id: String(node.id || ""),
        label: String(node.label || node.id || "Draft logic node"),
        op: String(node.op || "and"),
        ruleCount: String(node.ruleCount || node.rule_count || "0"),
        evidence: String(node.evidence || "evidence_gap"),
        sourceRef: String(node.sourceRef || node.source_ref || "ui_draft.import"),
        op_catalog_entry: String(node.op_catalog_entry || node.opCatalogEntry || node.op || "and"),
        rules: Array.isArray(node.rules) ? node.rules : [],
        hardware_binding: node.hardware_binding || node.hardwareBinding || {},
        port_contract: node.port_contract || node.portContract || null,
        component_template: node.component_template || node.componentTemplate || null,
        subsystem_group: node.subsystem_group || node.subsystemGroup || null,
        x: String(node.x || "50%"),
        y: String(node.y || "50%"),
        draftNode: Boolean(node.draftNode || node.draft_node || String(node.id || "").startsWith("draft_node_")),
      })),
      edges: Array.isArray(validated.edges) ? validated.edges : [],
    });
    if (draftLabel) {
      draftLabel.textContent = "sandbox_candidate restored from imported JSON";
    }
    if (draftJsonStatus) {
      draftJsonStatus.textContent = "sandbox_candidate restored from imported JSON";
    }
    setTimelineState("derived");
    persistDraft();
    return validated;
  }

  function exportEditableDraftJson() {
    if (!draftJsonBuffer) return null;
    const payload = buildEditableDraftExport();
    draftJsonBuffer.value = JSON.stringify(payload, null, 2);
    if (draftJsonStatus) {
      draftJsonStatus.textContent =
        "Exported sandbox_candidate draft JSON. Truth-level impact: none.";
    }
    return payload;
  }

  function exportWorkbenchInterfaceMatrix() {
    const snapshot = currentDraftSnapshot();
    const matrix = snapshot.interface_matrix || buildWorkbenchInterfaceMatrix(
      snapshot.hardware_bindings || [],
      snapshot.typed_ports || [],
      snapshot.hardware_binding_diagnostics,
      snapshot.binding_coverage,
    );
    if (interfaceMatrixOutput) {
      interfaceMatrixOutput.value = JSON.stringify(matrix, null, 2);
    }
    clearInterfaceMatrixValidationReport();
    if (interfaceMatrixStatus) {
      interfaceMatrixStatus.textContent =
        `Exported ${matrix.row_count || 0} interface row(s), ${matrix.evidence_gap_field_count || 0} evidence-gap field(s). Truth effect: none.`;
    }
    return matrix;
  }

  function validateInterfaceMatrixImportPayload(payload) {
    if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
      throw new Error("interface matrix JSON must be an object");
    }
    if (payload.kind !== "well-harness-workbench-interface-matrix") {
      throw new Error("interface matrix kind must be well-harness-workbench-interface-matrix");
    }
    if (payload.truth_effect !== "none") {
      throw new Error("interface matrix truth_effect must be none");
    }
    if (!Array.isArray(payload.rows)) {
      throw new Error("interface matrix rows must be an array");
    }
    for (const row of payload.rows) {
      if (!row || typeof row !== "object" || Array.isArray(row)) {
        throw new Error("interface matrix row must be an object");
      }
      if (row.truth_effect !== "none") {
        throw new Error("interface matrix row truth_effect must be none");
      }
    }
    return payload;
  }

  function interfaceBindingFromMatrixRow(row) {
    return normalizeInterfaceBinding({
      hardware_id: row.hardware_id,
      cable: row.cable,
      connector: row.connector,
      port_local: row.port_local,
      port_peer: row.port_peer,
      evidence_status: row.evidence_status,
      source_ref: row.source_ref || `ui_draft.interface_matrix.${row.owner_kind || "unknown"}.${row.owner_id || "unknown"}`,
    }, row.owner_kind, row.owner_id);
  }

  const interfaceMatrixSpreadsheetColumns = [
    "row_id",
    "owner_kind",
    "owner_id",
    "hardware_id",
    "cable",
    "connector",
    "port_local",
    "port_peer",
    "evidence_status",
    "truth_effect",
    "source_ref",
  ];

  function spreadsheetCellValue(value, fallback) {
    const text = value === null || value === undefined ? "" : String(value).trim();
    return text || fallback;
  }

  function escapeDelimitedCell(value, delimiter) {
    const text = value === null || value === undefined ? "" : String(value);
    if (
      text.includes("\"")
      || text.includes("\t")
      || text.includes("\n")
      || text.includes("\r")
      || text.includes(delimiter)
      || text.trim() !== text
    ) {
      return `"${text.replace(/"/g, "\"\"")}"`;
    }
    return text;
  }

  function interfaceMatrixToDelimitedText(matrix, delimiter) {
    const rows = matrix && Array.isArray(matrix.rows) ? matrix.rows : [];
    return [
      interfaceMatrixSpreadsheetColumns.join(delimiter),
      ...rows.map((row) => interfaceMatrixSpreadsheetColumns
        .map((column) => escapeDelimitedCell(row && row[column] !== undefined ? row[column] : "", delimiter))
        .join(delimiter)),
    ].join("\n");
  }

  function delimiterCountOutsideQuotes(line, delimiter) {
    let count = 0;
    let inQuotes = false;
    for (let index = 0; index < line.length; index += 1) {
      const char = line[index];
      if (char === "\"") {
        if (inQuotes && line[index + 1] === "\"") {
          index += 1;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (!inQuotes && char === delimiter) {
        count += 1;
      }
    }
    return count;
  }

  function detectSpreadsheetDelimiter(text) {
    const firstLine = String(text || "").split(/\r?\n/).find((line) => line.trim()) || "";
    const tabCount = delimiterCountOutsideQuotes(firstLine, "\t");
    const commaCount = delimiterCountOutsideQuotes(firstLine, ",");
    return tabCount > commaCount ? "\t" : ",";
  }

  function parseDelimitedRecords(text, delimiter) {
    const records = [];
    let row = [];
    let cell = "";
    let inQuotes = false;
    const source = String(text || "");
    for (let index = 0; index < source.length; index += 1) {
      const char = source[index];
      if (char === "\"") {
        if (inQuotes && source[index + 1] === "\"") {
          cell += "\"";
          index += 1;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (!inQuotes && char === delimiter) {
        row.push(cell);
        cell = "";
      } else if (!inQuotes && (char === "\n" || char === "\r")) {
        if (char === "\r" && source[index + 1] === "\n") index += 1;
        row.push(cell);
        if (row.some((value) => String(value).trim())) records.push(row);
        row = [];
        cell = "";
      } else {
        cell += char;
      }
    }
    row.push(cell);
    if (row.some((value) => String(value).trim())) records.push(row);
    if (inQuotes) throw new Error("interface matrix CSV has an unterminated quoted field");
    return records;
  }

  function normalizeSpreadsheetHeader(value) {
    return String(value || "").replace(/^\uFEFF/, "").trim().toLowerCase().replace(/[\s-]+/g, "_");
  }

  function interfaceMatrixFromDelimitedText(text) {
    const source = String(text || "").trim();
    if (!source) throw new Error("interface matrix CSV is empty");
    const delimiter = detectSpreadsheetDelimiter(source);
    const records = parseDelimitedRecords(source, delimiter);
    if (records.length < 2) {
      throw new Error("interface matrix CSV requires a header row and at least one data row");
    }
    const headers = records[0].map(normalizeSpreadsheetHeader);
    const headerIndex = new Map(headers.map((header, index) => [header, index]));
    const requiredHeaders = ["owner_kind", "owner_id"];
    const missingHeaders = requiredHeaders.filter((header) => !headerIndex.has(header));
    if (missingHeaders.length) {
      throw new Error(`interface matrix CSV missing required column(s): ${missingHeaders.join(", ")}`);
    }
    const readCell = (record, column, fallback) => {
      const index = headerIndex.get(column);
      return spreadsheetCellValue(index === undefined ? "" : record[index], fallback);
    };
    const rows = records.slice(1).map((record, index) => {
      const ownerKind = readCell(record, "owner_kind", "evidence_gap");
      const ownerId = readCell(record, "owner_id", "evidence_gap");
      return {
        row_id: readCell(record, "row_id", `interface:csv:${String(index + 1).padStart(2, "0")}`),
        owner_kind: ownerKind,
        owner_id: ownerId,
        hardware_id: readCell(record, "hardware_id", "evidence_gap"),
        cable: readCell(record, "cable", "evidence_gap"),
        connector: readCell(record, "connector", "evidence_gap"),
        port_local: readCell(record, "port_local", "evidence_gap"),
        port_peer: readCell(record, "port_peer", "evidence_gap"),
        evidence_status: readCell(record, "evidence_status", "evidence_gap"),
        truth_effect: readCell(record, "truth_effect", "none"),
        source_ref: readCell(record, "source_ref", `ui_draft.interface_matrix_csv.${ownerKind}.${ownerId}`),
      };
    });
    return {
      kind: "well-harness-workbench-interface-matrix",
      version: 1,
      system_id: "thrust-reverser",
      matrix_scope: "sandbox_candidate_interface_design",
      row_count: rows.length,
      rows,
      truth_effect: "none",
    };
  }

  function currentInterfaceMatrixPayloadForSpreadsheet() {
    if (interfaceMatrixOutput && interfaceMatrixOutput.value.trim()) {
      const parsed = JSON.parse(interfaceMatrixOutput.value);
      return validateInterfaceMatrixImportPayload(parsed);
    }
    return exportWorkbenchInterfaceMatrix();
  }

  function exportWorkbenchInterfaceMatrixCsv() {
    if (!interfaceMatrixCsvOutput) return null;
    try {
      const matrix = currentInterfaceMatrixPayloadForSpreadsheet();
      interfaceMatrixCsvOutput.value = interfaceMatrixToDelimitedText(matrix, ",");
      if (interfaceMatrixStatus) {
        interfaceMatrixStatus.textContent =
          `Exported ${matrix.row_count || 0} spreadsheet row(s). Truth effect: none.`;
      }
      return matrix;
    } catch (err) {
      if (interfaceMatrixStatus) {
        interfaceMatrixStatus.textContent =
          err && err.message ? err.message : "interface matrix CSV export failed";
      }
      return null;
    }
  }

  function importWorkbenchInterfaceMatrixCsv() {
    if (!interfaceMatrixCsvOutput || !interfaceMatrixOutput) return null;
    try {
      const matrix = interfaceMatrixFromDelimitedText(interfaceMatrixCsvOutput.value || "");
      interfaceMatrixOutput.value = JSON.stringify(matrix, null, 2);
      const report = validateWorkbenchInterfaceMatrix();
      if (interfaceMatrixStatus) {
        interfaceMatrixStatus.textContent =
          `Imported ${matrix.row_count || 0} spreadsheet row(s). Matrix validation ${report ? report.status : "not_run"}. Truth effect: none.`;
      }
      return matrix;
    } catch (err) {
      renderInterfaceMatrixValidationReport(emptyInterfaceMatrixValidationReport(
        "fail",
        err && err.message ? err.message : "interface matrix CSV import failed",
      ), { updateStatus: false });
      if (interfaceMatrixStatus) {
        interfaceMatrixStatus.textContent =
          err && err.message ? err.message : "interface matrix CSV import failed";
      }
      return null;
    }
  }

  function applyInterfaceMatrixRows(rows, validationRows, selectedRowIds) {
    let applied = 0;
    let skipped = 0;
    let noop = 0;
    let deselected = 0;
    let rejected = 0;
    const reports = Array.isArray(validationRows) ? validationRows : [];
    const hasValidationRows = reports.length > 0;
    const hasSelectedRows = selectedRowIds instanceof Set;
    refreshEditableNodes();
    for (let index = 0; index < rows.length; index += 1) {
      const row = rows[index];
      const report = hasValidationRows ? reports[index] : null;
      if (report && report.status === "reject") {
        rejected += 1;
        continue;
      }
      if (report && report.status === "no_op") {
        noop += 1;
        continue;
      }
      if (report && report.status === "skipped") {
        skipped += 1;
        continue;
      }
      if (hasValidationRows && (!report || report.action !== "apply")) {
        skipped += 1;
        continue;
      }
      if (report && report.status === "applyable" && report.action === "apply" && hasSelectedRows) {
        const rowId = normalizedInterfaceField(report.row_id || row.row_id);
        if (!selectedRowIds.has(rowId)) {
          deselected += 1;
          continue;
        }
      }
      const ownerKind = normalizedInterfaceField(row.owner_kind);
      const ownerId = normalizedInterfaceField(row.owner_id);
      const binding = interfaceBindingFromMatrixRow(row);
      if (ownerKind === "node") {
        const node = nodes.find((candidate) => editableNodeId(candidate) === ownerId);
        if (!node) {
          skipped += 1;
          continue;
        }
        setNodeInterfaceBinding(node, binding);
        applied += 1;
        continue;
      }
      if (ownerKind === "edge") {
        const edge = draftEdges.find((candidate) => (
          candidate.id === ownerId
          || `${candidate.source || "unknown"}->${candidate.target || "unknown"}` === ownerId
        ));
        if (!edge) {
          skipped += 1;
          continue;
        }
        setEdgeInterfaceBinding(edge, binding);
        applied += 1;
        continue;
      }
      skipped += 1;
    }
    return { applied, skipped, noop, deselected, rejected };
  }

  function selectedInterfaceMatrixApplyableRowCount(report, selectedRowIds) {
    const rows = report && Array.isArray(report.rows) ? report.rows : [];
    const hasSelectedRows = selectedRowIds instanceof Set;
    return rows.filter((row) => (
      normalizedInterfaceField(row.status) === "applyable"
      && normalizedInterfaceField(row.action || "none") === "apply"
      && (!hasSelectedRows || selectedRowIds.has(normalizedInterfaceField(row.row_id)))
    )).length;
  }

  function applyWorkbenchInterfaceMatrix() {
    if (!interfaceMatrixOutput) return null;
    try {
      const parsedPayload = JSON.parse(interfaceMatrixOutput.value || "{}");
      const selectedRowIds = interfaceMatrixSelectedApplyRowIdsFromReview();
      const report = buildInterfaceMatrixValidationReport(parsedPayload);
      renderInterfaceMatrixValidationReport(report, { updateStatus: false, selectedRowIds });
      if (report.status === "fail") {
        if (interfaceMatrixStatus) {
          const firstError = (report.issues || []).find((issue) => issue.severity === "error");
          interfaceMatrixStatus.textContent =
            [
              `Matrix validation failed: ${report.issue_count || 0} issue(s).`,
              firstError && firstError.message,
              "No sandbox bindings were changed.",
            ].filter(Boolean).join(" ");
        }
        return null;
      }
      const payload = validateInterfaceMatrixImportPayload(parsedPayload);
      if (selectedInterfaceMatrixApplyableRowCount(report, selectedRowIds) > 0) {
        recordEditableHistory("interface_matrix_apply");
        shell.setAttribute("data-draft-state", "derived");
      }
      const summary = applyInterfaceMatrixRows(payload.rows, report.rows, selectedRowIds);
      if (summary.applied > 0) {
        if (draftLabel) draftLabel.textContent = "sandbox_candidate interface matrix applied";
        renderEditableEdges();
        renderInspector();
        validateEditableGraph();
        updateEditableDraftHash();
        persistDraft();
      }
      const matrix = exportWorkbenchInterfaceMatrix();
      validateWorkbenchInterfaceMatrix({ updateStatus: false });
      if (interfaceMatrixStatus) {
        interfaceMatrixStatus.textContent =
          `Applied ${summary.applied} matrix row(s), deselected ${summary.deselected}, no-op ${summary.noop}, skipped ${summary.skipped}. Export now has ${matrix.row_count || 0} row(s). Truth effect: none.`;
      }
      return summary;
    } catch (err) {
      renderInterfaceMatrixValidationReport(emptyInterfaceMatrixValidationReport(
        "fail",
        err && err.message ? err.message : "interface matrix import failed",
      ), { updateStatus: false });
      if (interfaceMatrixStatus) {
        interfaceMatrixStatus.textContent =
          err && err.message ? err.message : "interface matrix import failed";
      }
      return null;
    }
  }

  function importEditableDraftJson() {
    if (!draftJsonBuffer) return null;
    try {
      const payload = JSON.parse(draftJsonBuffer.value || "{}");
      return applyEditableDraftImport(payload);
    } catch (err) {
      if (draftJsonStatus) {
        draftJsonStatus.textContent =
          err && err.message ? err.message : "draft JSON import failed";
      }
      return null;
    }
  }

  function firstDivergenceText(firstDivergence) {
    if (!firstDivergence) return "No divergence recorded.";
    const signal = firstDivergence.signal_id || "unknown_signal";
    const atS = firstDivergence.at_s;
    const baseline = firstDivergence.baseline_value;
    const candidate = firstDivergence.candidate_value;
    return `${signal} @ ${atS}s · baseline=${baseline} candidate=${candidate}`;
  }

  function graphValidationReportText(report) {
    if (!report || !report.categories) return "";
    const order = ["missing_node", "invalid_edge", "dangling_port", "duplicate_edge", "unsafe_op"];
    const parts = order
      .map((category) => {
        const issues = report.categories[category] || [];
        return issues.length ? `${category}: ${issues.length}` : "";
      })
      .filter(Boolean);
    if (!parts.length) return "graph validation: no issues";
    return `graph validation: ${parts.join(", ")}`;
  }

  function buildWorkbenchGateClaims() {
    return {
      default_pytest: "required",
      gsd_validation: "required",
      adversarial: "required",
      e2e_49_49: "not_claimed",
      mypy_strict_clean: "not_claimed",
    };
  }

  function buildWorkbenchKnownBlockers() {
    return [
      {
        gate: "e2e 49/49",
        status: "not_claimed_clean",
        evidence: "Workbench archive is local draft evidence; e2e 49/49 is not claimed from this UI export.",
        truth_effect: "none",
      },
      {
        gate: "PYTHONPATH=src:. python3 tools/run_mypy_gate.py --format json",
        status: "known_baseline_blocker",
        evidence: "JER-171 defines the official mypy evidence command; current full-repo strict gate is blocked, not clean.",
        truth_effect: "none",
      },
    ];
  }

  function summarizeRepairActionsForProofPacket(actions) {
    const rows = repairActionLogSnapshotFromSource(actions);
    return {
      action_count: rows.length,
      action_ids: rows.map((entry) => entry.action_id),
      last_action_id: rows.length ? rows[rows.length - 1].action_id : null,
      checksum: checksumEvidenceArchiveField(rows),
      truth_effect: "none",
    };
  }

  function repairActionLogSnapshotFromSource(actions) {
    return normalizeRepairActionLog(Array.isArray(actions) ? actions : []);
  }

  function proofPacketBindingDiagnosticsSummary(diagnostics) {
    const source = diagnostics && typeof diagnostics === "object" ? diagnostics : {};
    return {
      status: normalizedInterfaceField(source.status || "unknown"),
      issue_count: Number.isFinite(Number(source.issue_count)) ? Number(source.issue_count) : 0,
      evidence_gap_field_count: Number.isFinite(Number(source.evidence_gap_field_count))
        ? Number(source.evidence_gap_field_count)
        : 0,
      checksum: checksumEvidenceArchiveField(source),
      truth_effect: "none",
    };
  }

  function proofPacketDiagnosticFocusSummary(focus) {
    const source = focus && typeof focus === "object" ? focus : currentDiagnosticFocusSummary();
    if (source.state === "selected") {
      return {
        ...normalizeHardwareBindingFocusTarget(source),
        state: "selected",
        truth_effect: "none",
      };
    }
    return {
      state: "none",
      truth_effect: "none",
    };
  }

  function buildChangeRequestProofPacket(snapshot, changedModelHash) {
    const sourceSnapshot = snapshot || currentDraftSnapshot();
    const hardwareBindings = sourceSnapshot.hardware_bindings || [];
    const bindingCoverage =
      sourceSnapshot.binding_coverage || buildInterfaceBindingCoverageSummary(hardwareBindings);
    const hardwareBindingDiagnostics =
      sourceSnapshot.hardware_binding_diagnostics || buildHardwareBindingDiagnosticsReport(hardwareBindings);
    const interfaceMatrix =
      sourceSnapshot.interface_matrix || buildWorkbenchInterfaceMatrix(
        hardwareBindings,
        sourceSnapshot.typed_ports || [],
        hardwareBindingDiagnostics,
        bindingCoverage,
      );
    const interfaceMatrixValidation =
      sourceSnapshot.interface_matrix_validation || lastInterfaceMatrixValidationReport || null;
    const matrixValidationSummary = interfaceMatrixValidationSummary(interfaceMatrixValidation);
    const connectorPinMap =
      sourceSnapshot.connector_pin_map || buildWorkbenchConnectorPinMap(hardwareBindings);
    const hardwareInterfaceDesigner =
      sourceSnapshot.hardware_interface_designer || currentHardwareInterfaceDesignerPayload("proof");
    const hardwareInterfaceDesignerValidation =
      sourceSnapshot.hardware_interface_designer_validation
      || currentHardwareInterfaceDesignerValidationReport("proof");
    const hardwareEvidenceV2 =
      sourceSnapshot.hardware_evidence_v2 || currentHardwareEvidenceV2Report();
    const selectedDebugTimeline =
      sourceSnapshot.selected_debug_timeline || currentSelectedDebugTimelinePacket("proof");
    const candidateBaselineDiffReviewV2 =
      currentCandidateBaselineDiffReviewV2Report("proof", changedModelHash);
    const preflightAnalyzerReport =
      sourceSnapshot.preflight_analyzer_report || currentPreflightAnalyzerReport("proof");
    const repairActions = repairActionLogSnapshotFromSource(sourceSnapshot.repair_action_log || []);
    const portContractSummary =
      sourceSnapshot.port_contract_summary || buildPortContractSummary(
        sourceSnapshot.typed_ports || [],
        sourceSnapshot.edges || [],
      );
    const portCompatibilityReport =
      sourceSnapshot.port_compatibility_report || buildPortCompatibilityReport(
        sourceSnapshot.typed_ports || [],
        sourceSnapshot.edges || [],
      );
    const operationCatalog = sourceSnapshot.operation_catalog || buildOperationCatalogSummary();
    const ruleParameterSummary = sourceSnapshot.rule_parameter_summary || buildRuleParameterSummary();
    const draftSnapshotManifest = buildDraftSnapshotManifestSummary();
    const diffVerdict = (lastSandboxDiff && lastSandboxDiff.verdict) || "not_run";
    const diagnosticsSummary = proofPacketBindingDiagnosticsSummary(hardwareBindingDiagnostics);
    const diagnosticFocusSummary = proofPacketDiagnosticFocusSummary(sourceSnapshot.diagnostic_focus);
    const repairActionLogSummary = summarizeRepairActionsForProofPacket(repairActions);
    return {
      kind: "well-harness-workbench-changerequest-proof-packet",
      version: 1,
      linear: {
        issue: "JER-TBD",
        project: "AI FANTUI LogicMVP · Editable Workbench v4 Authoring + Hardware Design",
        live_mutation: false,
        agent_eligible: "No",
      },
      adapter: "thrust-reverser",
      layer: "L4",
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_level_impact: "none",
      dal_pssa_impact: "none",
      red_lines_touched: "none",
      controller_truth_modified: false,
      frozen_assets_modified: false,
      truth_effect: "none",
      changed_model_hash: changedModelHash || editableDraftHash(stableEvidenceArchiveJson(sourceSnapshot)),
      selected_scenario_id: selectedWorkbenchScenarioId(),
      selected_node_id: sourceSnapshot.selected_node && sourceSnapshot.selected_node.id
        ? sourceSnapshot.selected_node.id
        : "unknown",
      sandbox_diff: {
        verdict: diffVerdict,
        scenario_id: (lastSandboxDiff && lastSandboxDiff.scenario_id) || selectedWorkbenchScenarioId(),
        first_divergence: (
          lastSandboxDiff
          && lastSandboxDiff.summary
          && lastSandboxDiff.summary.first_divergence
        ) || null,
        truth_level_impact: "none",
      },
      hardware_binding_summary: {
        binding_count: hardwareBindings.length,
        coverage: {
          complete: bindingCoverage.complete,
          partial: bindingCoverage.partial,
          missing: bindingCoverage.missing,
        },
        checksum: checksumEvidenceArchiveField(hardwareBindings),
        truth_effect: "none",
      },
      diagnostics: {
        hardware_binding: diagnosticsSummary,
        truth_effect: "none",
      },
      hardware_binding_diagnostics_summary: diagnosticsSummary,
      interface_matrix_summary: {
        row_count: interfaceMatrix.row_count || 0,
        typed_port_count: interfaceMatrix.typed_port_count || 0,
        evidence_gap_field_count: interfaceMatrix.evidence_gap_field_count || 0,
        diagnostics_status: interfaceMatrix.diagnostics_status || "unknown",
        checksum: checksumEvidenceArchiveField(interfaceMatrix),
        truth_effect: "none",
      },
      interface_matrix_validation_summary: matrixValidationSummary,
      connector_pin_map_summary: {
        row_count: connectorPinMap.row_count || 0,
        evidence_gap_field_count: connectorPinMap.evidence_gap_field_count || 0,
        checksum: checksumEvidenceArchiveField(connectorPinMap),
        truth_effect: "none",
      },
      hardware_interface_designer_summary: {
        lru_count: (hardwareInterfaceDesigner.lrus || []).length,
        cable_count: (hardwareInterfaceDesigner.cables || []).length,
        connector_count: (hardwareInterfaceDesigner.connectors || []).length,
        port_count: (hardwareInterfaceDesigner.ports || []).length,
        pin_count: (hardwareInterfaceDesigner.pins || []).length,
        binding_count: (hardwareInterfaceDesigner.bindings || []).length,
        validation_status: hardwareInterfaceDesignerValidation.status || "pass",
        finding_count: hardwareInterfaceDesignerValidation.finding_count || 0,
        checksum: checksumEvidenceArchiveField(hardwareInterfaceDesigner),
        validation_checksum: checksumEvidenceArchiveField(hardwareInterfaceDesignerValidation),
        truth_effect: "none",
      },
      hardware_evidence_v2_summary: {
        target: `${hardwareEvidenceV2.target_kind || "none"}:${hardwareEvidenceV2.target_id || "none"}`,
        coverage_status: hardwareEvidenceV2.coverage_status || "missing",
        selected_gap_count: hardwareEvidenceV2.evidence_gap_count || 0,
        reference_signal_count: hardwareEvidenceV2.reference_signal_count || 0,
        connector_pin_row_count: hardwareEvidenceV2.connector_pin_row_count || 0,
        checksum: checksumEvidenceArchiveField(hardwareEvidenceV2),
        truth_effect: "none",
      },
      selected_debug_timeline_summary: {
        target: selectedDebugTimeline.owner_key || "none:none",
        scenario_id: selectedDebugTimeline.scenario_id || selectedWorkbenchScenarioId(),
        diff_verdict: selectedDebugTimeline.diff_verdict || "not_run",
        trace_link_status: selectedDebugTimeline.trace_link_status || "selection_only",
        hardware_id: (
          selectedDebugTimeline.hardware_overlay
          && selectedDebugTimeline.hardware_overlay.hardware_id
        ) || "evidence_gap",
        checksum: checksumEvidenceArchiveField(selectedDebugTimeline),
        truth_effect: "none",
      },
      candidate_baseline_diff_review_v2_summary: {
        verdict: candidateBaselineDiffReviewV2.verdict || "not_run",
        review_readiness: candidateBaselineDiffReviewV2.review_readiness || "run_required",
        archive_state: candidateBaselineDiffReviewV2.archive_state || "not_archive_ready",
        scenario_id: candidateBaselineDiffReviewV2.scenario_id || selectedWorkbenchScenarioId(),
        selected_target: candidateBaselineDiffReviewV2.selected_target || "none:none",
        first_divergence_text: candidateBaselineDiffReviewV2.first_divergence_text || "not run",
        certification_claim: candidateBaselineDiffReviewV2.certification_claim || "none",
        checksum: checksumEvidenceArchiveField(candidateBaselineDiffReviewV2),
        truth_effect: "none",
      },
      preflight_analyzer_summary: {
        classification: preflightAnalyzerReport.classification || "needs_evidence",
        finding_count: preflightAnalyzerReport.finding_count || 0,
        sandbox_report_freshness: preflightAnalyzerReport.sandbox_report_freshness || "missing",
        candidate_model_hash: preflightAnalyzerReport.candidate_model_hash || "unavailable",
        checksum: checksumEvidenceArchiveField(preflightAnalyzerReport),
        truth_effect: "none",
      },
      selected_focus: diagnosticFocusSummary,
      diagnostic_focus: diagnosticFocusSummary,
      repair_action_log_summary: repairActionLogSummary,
      repair_action_log_summary_checksum: repairActionLogSummary.checksum,
      repair_action_summary: repairActionLogSummary,
      port_contract_summary: {
        total_ports: portContractSummary.total_ports,
        edge_contracts: portContractSummary.edge_contracts,
        required_ports: portContractSummary.required_ports,
        truth_effect: "none",
      },
      port_compatibility_summary: {
        status: portCompatibilityReport.status,
        warning_count: portCompatibilityReport.warning_count,
        error_count: portCompatibilityReport.error_count,
        truth_effect: "none",
      },
      operation_catalog: {
        version: operationCatalog.version,
        selected_op: operationCatalog.selected_op,
        approved_ops: operationCatalog.approved_ops || [],
        truth_effect: "none",
      },
      rule_parameter_summary: {
        total_rules: ruleParameterSummary.total_rules,
        touched_nodes: ruleParameterSummary.touched_nodes || [],
        truth_effect: "none",
      },
      draft_snapshot_manifest: {
        snapshot_count: draftSnapshotManifest.snapshot_count,
        active_snapshot_id: draftSnapshotManifest.active_snapshot_id,
        truth_effect: "none",
      },
      gate_claims: buildWorkbenchGateClaims(),
      known_blockers: buildWorkbenchKnownBlockers(),
      required_test_evidence: [
        "targeted pytest",
        "default pytest",
        "GSD validation suite",
        "adversarial 8/8",
        "full e2e status with known blockers declared",
        "mypy gate status with JER-171 blocker declared",
      ],
    };
  }

  function proofPacketBindingSummaryText(packet) {
    const summary = packet.hardware_binding_summary || {};
    const coverage = summary.coverage || {};
    return `${summary.binding_count || 0} binding(s) / ${coverage.complete || 0} complete / ${coverage.partial || 0} partial / ${coverage.missing || 0} missing`;
  }

  function proofPacketDiagnosticsText(packet) {
    const summary = packet.hardware_binding_diagnostics_summary || {};
    return `${summary.status || "unknown"} / issues=${summary.issue_count || 0} / gaps=${summary.evidence_gap_field_count || 0}`;
  }

  function proofPacketInterfaceMatrixText(packet) {
    const summary = packet.interface_matrix_summary || {};
    return `${summary.row_count || 0} row(s) / typed_ports=${summary.typed_port_count || 0} / gaps=${summary.evidence_gap_field_count || 0}`;
  }

  function proofPacketInterfaceMatrixValidationText(packet) {
    const summary = packet.interface_matrix_validation_summary || {};
    return `${summary.status || "not_run"} / applyable=${summary.applyable_row_count || 0} / skipped=${summary.skipped_row_count || 0} / issues=${summary.issue_count || 0}`;
  }

  function proofPacketConnectorPinMapText(packet) {
    const summary = packet.connector_pin_map_summary || {};
    return `${summary.row_count || 0} row(s) / gaps=${summary.evidence_gap_field_count || 0}`;
  }

  function proofPacketHardwareEvidenceV2Text(packet) {
    const summary = packet.hardware_evidence_v2_summary || {};
    return `${summary.target || "none"} / ${summary.coverage_status || "missing"} / selected gaps=${summary.selected_gap_count || 0} / reference signals=${summary.reference_signal_count || 0}`;
  }

  function proofPacketSelectedDebugTimelineText(packet) {
    const summary = packet.selected_debug_timeline_summary || {};
    return `${summary.target || "none"} / ${summary.scenario_id || "nominal_landing"} / ${summary.diff_verdict || "not_run"} / ${summary.trace_link_status || "selection_only"}`;
  }

  function proofPacketDiffReviewV2Text(packet) {
    const summary = packet.candidate_baseline_diff_review_v2_summary || {};
    return `${summary.verdict || "not_run"} / ${summary.review_readiness || "run_required"} / ${summary.archive_state || "not_archive_ready"} / claim=${summary.certification_claim || "none"}`;
  }

  function proofPacketPreflightAnalyzerText(packet) {
    const summary = packet.preflight_analyzer_summary || {};
    return `${summary.classification || "needs_evidence"} / findings=${summary.finding_count || 0} / freshness=${summary.sandbox_report_freshness || "missing"}`;
  }

  function proofPacketDiagnosticFocusText(packet) {
    const focus = packet.selected_focus || packet.diagnostic_focus || {};
    if (focus.state !== "selected") return "none";
    return `${focus.target_kind}:${focus.target_id}${focus.edge_index !== undefined ? `#${focus.edge_index}` : ""} / ${focus.rule_id || "hardware_binding_diagnostic"}`;
  }

  function proofPacketRepairActionText(packet) {
    const summary = packet.repair_action_log_summary || packet.repair_action_summary || {};
    return `${summary.action_count || 0} sandbox repair action(s) / checksum=${summary.checksum || "none"}`;
  }

  function buildChangeRequestTestDeltaPlaceholders() {
    return {
      targeted_pytest: "pending",
      default_pytest: "pending",
      gsd_validation_suite: "pending",
      adversarial_8_8: "pending",
      e2e_49_49: "not_claimed",
      mypy_strict_clean: "not_claimed",
      truth_effect: "none",
    };
  }

  function buildChangeRequestHandoffPacket(proofPacket, linearIssueBody, prProofPacket) {
    const packet = proofPacket || buildChangeRequestProofPacket();
    const linearBody = linearIssueBody || linearIssueBodyFromProofPacket(packet);
    const prBody = prProofPacket || prProofTextFromProofPacket(packet);
    const testDelta = buildChangeRequestTestDeltaPlaceholders();
    return {
      "$schema": "https://well-harness.local/json_schema/workbench_changerequest_handoff_v1.schema.json",
      kind: "well-harness-workbench-changerequest-handoff-packet",
      version: 1,
      packet_state: "draft",
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_effect: "none",
      live_linear_mutation: false,
      controller_truth_modified: false,
      frozen_assets_modified: false,
      truth_level_impact: "none",
      dal_pssa_impact: "none",
      red_lines_touched: "none",
      artifact_scope: "browser_local_draft",
      truth_scope: "evidence_only",
      runtime_mutates_truth: false,
      serialization: {
        canonicalization: "json.sort_keys.separators.v1",
        checksum_algorithm: "ui_fnv1a32_over_canonical_json",
      },
      outcome:
        `Review sandbox candidate edit for ${packet.selected_node_id || "selected node"} against the certified thrust-reverser baseline.`,
      context:
        "Generated by /workbench from a sandbox candidate and evidence archive. This packet prepares a ChangeRequest review only.",
      acceptance: [
        "Candidate draft hash is recorded.",
        "Baseline diff evidence is attached before implementation.",
        "Hardware/interface evidence and evidence gaps are explicit.",
        "Reviewer confirms no certified truth, DAL, PSSA, frozen adapter, or controller semantics changed.",
      ],
      boundaries: [
        "No live Linear mutation from the workbench.",
        "No controller.py truth semantics edit.",
        "No frozen adapter, frozen hardware YAML, or C919 reference packet change.",
        "No truth-level, DAL, or PSSA promotion.",
      ],
      evidence_required: [
        "Editable draft JSON export.",
        "Sandbox baseline diff report.",
        "Candidate-to-baseline Diff Review v2 report.",
        "Selected graph timeline/debug packet.",
        "Hardware Evidence Inspector v2 selected-owner packet.",
        "Connector/pin map export.",
        "Interface matrix export and validation preview.",
        "Workbench preflight analyzer report.",
        "Structured ChangeRequest proof packet.",
        "PR proof packet with test delta.",
      ],
      red_line_metadata: {
        red_lines_touched: "none",
        truth_level_impact: "none",
        dal_pssa_impact: "none",
        controller_truth_modified: false,
        frozen_assets_modified: false,
        live_linear_mutation: false,
      },
      metadata: {
        linear_issue: packet.linear && packet.linear.issue ? packet.linear.issue : "JER-TBD",
        linear_project: packet.linear && packet.linear.project
          ? packet.linear.project
          : "AI FANTUI LogicMVP · Editable Workbench v4 Authoring + Hardware Design",
        adapter: packet.adapter,
        layer: packet.layer,
        selected_scenario_id: packet.selected_scenario_id,
        selected_node_id: packet.selected_node_id,
        changed_model_hash: packet.changed_model_hash,
        sandbox_verdict: packet.sandbox_diff && packet.sandbox_diff.verdict,
        diff_review_v2: packet.candidate_baseline_diff_review_v2_summary || {},
        preflight_analyzer: packet.preflight_analyzer_summary || {},
        test_delta: testDelta,
        agent_eligible: "No",
      },
      artifacts: {
        linear_issue_body_checksum: checksumEvidenceArchiveField(linearBody),
        pr_proof_packet_checksum: checksumEvidenceArchiveField(prBody),
        changerequest_proof_packet_checksum: checksumEvidenceArchiveField(packet),
        diff_review_v2_checksum: (
          packet.candidate_baseline_diff_review_v2_summary
          && packet.candidate_baseline_diff_review_v2_summary.checksum
        ) || "not_available",
        preflight_analyzer_report_checksum: (
          packet.preflight_analyzer_summary
          && packet.preflight_analyzer_summary.checksum
        ) || "not_available",
      },
      linear_issue_body: linearBody,
      pr_proof_packet: prBody,
      changerequest_proof_packet: packet,
    };
  }

  function linearIssueBodyFromProofPacket(packet) {
    return [
      "## Outcome",
      `Review sandbox candidate edit for ${packet.selected_node_id || "selected node"} against the certified thrust-reverser baseline.`,
      "",
      "## Context",
      "Generated by /workbench Evidence Inspector from a sandbox candidate. No live Linear mutation.",
      "",
      "## Acceptance",
      "- Candidate draft hash is recorded.",
      "- Baseline diff evidence is attached before implementation.",
      "- Hardware/interface evidence and evidence gaps are explicit.",
      "- Reviewer confirms no certified truth, DAL, PSSA, frozen adapter, or controller semantics changed.",
      "",
      "## Boundaries",
      "- No live Linear mutation from the workbench.",
      "- No controller.py truth semantics edit.",
      "- No frozen adapter, frozen hardware YAML, C919 reference packet, truth-level, or DAL/PSSA change.",
      "",
      "## Evidence Required",
      "- Editable draft JSON export.",
      "- Sandbox baseline diff report.",
      "- Candidate-to-baseline Diff Review v2 report.",
      "- Selected graph timeline/debug packet.",
      "- Hardware/interface binding draft evidence.",
      "- Hardware Evidence Inspector v2 selected-owner packet.",
      "- Interface matrix export.",
      "- Binding coverage summary.",
      "- Hardware binding diagnostics report.",
      "- Selected binding diagnostic focus.",
      "- Diagnostic repair action log.",
      "- Workbench preflight analyzer report.",
      "- Structured ChangeRequest proof packet.",
      "- Interface matrix validation preview report.",
      "- Connector/pin map export.",
      "- Typed port contract summary.",
      "- Port compatibility report.",
      "- Operation catalog provenance.",
      "- Rule parameter summary.",
      "- Draft snapshot manifest.",
      "- Targeted pytest and PR proof packet.",
      "- Official mypy evidence command: PYTHONPATH=src:. python3 tools/run_mypy_gate.py --format json.",
      "- e2e 49/49 and mypy --strict clean are not claimed from this local UI archive.",
      "",
      "## Red Lines",
      `- Red lines touched: ${packet.red_lines_touched}`,
      "- controller.py truth semantics: not changed",
      "- frozen adapters / frozen YAML / C919 packet: not changed",
      "- truth-level / DAL / PSSA promotion: none",
      "- live Linear mutation: false",
      "",
      "## Test Delta",
      "- targeted pytest: pending",
      "- default pytest: pending",
      "- GSD validation suite: pending",
      "- adversarial 8/8: pending",
      "- e2e 49/49: not claimed",
      "- mypy --strict clean: not claimed",
      "",
      "## Metadata",
      `- Adapter: ${packet.adapter}`,
      `- Layer: ${packet.layer}`,
      `- Truth-level impact: ${packet.truth_level_impact}`,
      `- Red lines touched: ${packet.red_lines_touched}`,
      `- Candidate state: ${packet.candidate_state}`,
      `- Certification claim: ${packet.certification_claim}`,
      `- Changed model hash: ${packet.changed_model_hash}`,
      `- Selected scenario: ${packet.selected_scenario_id}`,
      `- Hardware/interface bindings: ${proofPacketBindingSummaryText(packet)}`,
      `- Interface matrix: ${proofPacketInterfaceMatrixText(packet)}`,
      `- Interface matrix validation: ${proofPacketInterfaceMatrixValidationText(packet)}`,
      `- Connector/pin map: ${proofPacketConnectorPinMapText(packet)}`,
      `- Hardware evidence v2: ${proofPacketHardwareEvidenceV2Text(packet)}`,
      `- Selected debug timeline: ${proofPacketSelectedDebugTimelineText(packet)}`,
      `- Diff review v2: ${proofPacketDiffReviewV2Text(packet)}`,
      `- Preflight analyzer: ${proofPacketPreflightAnalyzerText(packet)}`,
      `- Hardware binding diagnostics: ${proofPacketDiagnosticsText(packet)}`,
      `- Selected diagnostic focus: ${proofPacketDiagnosticFocusText(packet)}`,
      `- Diagnostic repair actions: ${proofPacketRepairActionText(packet)}`,
      `- Sandbox verdict: ${packet.sandbox_diff && packet.sandbox_diff.verdict}`,
      "- Agent eligible: No",
    ].join("\n");
  }

  function prProofTextFromProofPacket(packet) {
    return [
      `Linear: ${packet.linear && packet.linear.issue ? packet.linear.issue : "JER-TBD"}`,
      `Adapter: ${packet.adapter}`,
      `Layer: ${packet.layer}`,
      `Truth-level impact: ${packet.truth_level_impact}`,
      `Red lines touched: ${packet.red_lines_touched}`,
      "Test delta: targeted pytest pending / default pytest pending / GSD pending / e2e 49/49 not claimed / mypy --strict clean not claimed",
      "",
      `Candidate state: ${packet.candidate_state}`,
      `Certification claim: ${packet.certification_claim}`,
      `Changed model hash: ${packet.changed_model_hash}`,
      `Selected scenario: ${packet.selected_scenario_id}`,
      `Latest sandbox verdict: ${packet.sandbox_diff && packet.sandbox_diff.verdict}`,
      `Hardware/interface bindings: ${proofPacketBindingSummaryText(packet)}`,
      `Interface matrix: ${proofPacketInterfaceMatrixText(packet)}`,
      `Interface matrix validation: ${proofPacketInterfaceMatrixValidationText(packet)}`,
      `Connector/pin map: ${proofPacketConnectorPinMapText(packet)}`,
      `Hardware evidence v2: ${proofPacketHardwareEvidenceV2Text(packet)}`,
      `Selected debug timeline: ${proofPacketSelectedDebugTimelineText(packet)}`,
      `Diff review v2: ${proofPacketDiffReviewV2Text(packet)}`,
      `Preflight analyzer: ${proofPacketPreflightAnalyzerText(packet)}`,
      `Hardware binding diagnostics: ${proofPacketDiagnosticsText(packet)}`,
      `Selected diagnostic focus: ${proofPacketDiagnosticFocusText(packet)}`,
      `Diagnostic repair actions: ${proofPacketRepairActionText(packet)}`,
      `Proof packet checksum: ${checksumEvidenceArchiveField(packet)}`,
      "Mypy evidence command: PYTHONPATH=src:. python3 tools/run_mypy_gate.py --format json",
      "No live Linear mutation; this packet is copy-ready evidence only.",
    ].join("\n");
  }

  function emptyWorkbenchGraphValidationReport(status) {
    return {
      kind: "well-harness-workbench-graph-validation-report",
      version: 1,
      status: status || "fail",
      issue_count: 0,
      categories: {
        invalid_edge: [],
        dangling_port: [],
        duplicate_edge: [],
        unsafe_op: [],
        missing_node: [],
      },
      issues: [],
      truth_level_impact: "none",
    };
  }

  function renderWorkbenchSandboxDiff(payload) {
    lastSandboxDiff = payload || null;
    const verdict = (payload && payload.verdict) || "invalid_scenario";
    if (diffPanel) diffPanel.setAttribute("data-verdict", verdict);
    if (diffVerdict) diffVerdict.textContent = verdict;
    if (diffScenario) diffScenario.textContent = (payload && payload.scenario_id) || "nominal_landing";
    if (diffModelHash) {
      const hash = payload && payload.model_hash;
      diffModelHash.textContent = hash ? String(hash).slice(0, 16) : "unavailable";
    }
    if (diffFirstDivergence) {
      const summary = payload && payload.summary;
      if (verdict === "invalid_model" || verdict === "invalid_scenario") {
        const validationText = graphValidationReportText(payload && payload.validation_report);
        diffFirstDivergence.textContent = [
          (payload && payload.error) || verdict,
          validationText,
        ].filter(Boolean).join(" | ");
      } else {
        diffFirstDivergence.textContent = firstDivergenceText(summary && summary.first_divergence);
      }
    }
    renderCandidateBaselineDiffReviewV2("diff", payload && payload.model_hash, payload);
    setTimelineState("diff");
    if (handoffStatus) {
      handoffStatus.textContent =
        `Sandbox diff ${verdict}. Truth-level impact: none. No live Linear mutation.`;
    }
  }

  function runWorkbenchSandboxDiff() {
    if (!runSandboxBtn || typeof fetch !== "function") return Promise.resolve(null);
    runSandboxBtn.disabled = true;
    if (diffVerdict) diffVerdict.textContent = "running";
    setTimelineState("running");
    let customSnapshot = null;
    try {
      customSnapshot = parseWorkbenchCustomSnapshot();
    } catch (err) {
      const payload = {
        verdict: "invalid_model",
        scenario_id: selectedWorkbenchScenarioId(),
        truth_level_impact: "none",
        error: err && err.message ? err.message : "custom snapshot JSON invalid",
        scenario_metadata: currentWorkbenchScenarioMetadata(),
        validation_report: emptyWorkbenchGraphValidationReport("fail"),
        summary: { first_divergence: null, assertion_status: "not_run", frame_count: 0 },
      };
      renderWorkbenchSandboxDiff(payload);
      runSandboxBtn.disabled = false;
      return Promise.resolve(payload);
    }
    const requestBody = {
      scenario_id: selectedWorkbenchScenarioId(),
      draft: currentDraftSnapshot(),
    };
    if (customSnapshot) requestBody.custom_snapshot = customSnapshot;
    return fetch("/api/workbench/editable-sandbox-run", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(requestBody),
    })
      .then((response) => response.json())
      .then((payload) => {
        renderWorkbenchSandboxDiff(payload);
        return payload;
      })
      .catch((err) => {
        const payload = {
          verdict: "invalid_scenario",
          scenario_id: selectedWorkbenchScenarioId(),
          truth_level_impact: "none",
          error: err && err.message ? err.message : "sandbox run failed",
          scenario_metadata: currentWorkbenchScenarioMetadata(),
          validation_report: emptyWorkbenchGraphValidationReport("fail"),
          summary: { first_divergence: null, assertion_status: "not_run", frame_count: 0 },
        };
        renderWorkbenchSandboxDiff(payload);
        return payload;
      })
      .finally(() => {
        runSandboxBtn.disabled = false;
      });
  }

  function buildEditableHandoffPacket() {
    const snapshot = currentDraftSnapshot();
    const changedModelHash = editableDraftHash(stableEvidenceArchiveJson(snapshot));
    const hardwareBindings = snapshot.hardware_bindings || [];
    const bindingCoverage = snapshot.binding_coverage || buildInterfaceBindingCoverageSummary(hardwareBindings);
    const hardwareBindingDiagnostics = snapshot.hardware_binding_diagnostics
      || buildHardwareBindingDiagnosticsReport(hardwareBindings);
    const diagnosticFocus = snapshot.diagnostic_focus || currentDiagnosticFocusSummary();
    const diagnosticRepairActions = snapshot.repair_action_log || repairActionLogSnapshot();
    const portContractSummary = snapshot.port_contract_summary || buildPortContractSummary(
      snapshot.typed_ports || [],
      snapshot.edges || [],
    );
    const portCompatibilityReport = snapshot.port_compatibility_report || buildPortCompatibilityReport(
      snapshot.typed_ports || [],
      snapshot.edges || [],
    );
    const operationCatalog = snapshot.operation_catalog || buildOperationCatalogSummary();
    const componentLibrary = snapshot.component_library || buildComponentLibrarySummary();
    const subsystemGroupSummary = snapshot.subsystem_groups || subsystemGroupsSnapshot();
    const subsystemInterfaceContracts =
      snapshot.subsystem_interface_contracts || buildSubsystemInterfaceContractsSummary(subsystemGroupSummary);
    const ruleParameterSummary = snapshot.rule_parameter_summary || buildRuleParameterSummary();
    const draftSnapshotManifest = buildDraftSnapshotManifestSummary();
    const changeRequestProofPacket = buildChangeRequestProofPacket(snapshot, changedModelHash);
    const linearIssueBody = linearIssueBodyFromProofPacket(changeRequestProofPacket);
    const prProofPacket = prProofTextFromProofPacket(changeRequestProofPacket);
    const changeRequestHandoffPacket =
      buildChangeRequestHandoffPacket(changeRequestProofPacket, linearIssueBody, prProofPacket);
    return {
      changedModelHash,
      changerequest_proof_packet: changeRequestProofPacket,
      changerequest_handoff_packet: changeRequestHandoffPacket,
      linearIssueBody,
      prProofPacket,
      gateClaims: buildWorkbenchGateClaims(),
      knownBlockers: buildWorkbenchKnownBlockers(),
      hardwareBindingDiagnostics,
      diagnosticFocus,
      diagnosticRepairActions,
      portContractSummary,
      portCompatibilityReport,
      operationCatalog,
      componentLibrary,
      subsystemGroupSummary,
      subsystemInterfaceContracts,
      ruleParameterSummary,
      draftSnapshotManifest,
    };
  }

  function renderEditableHandoffPacket() {
    const packet = buildEditableHandoffPacket();
    if (linearHandoffOutput) linearHandoffOutput.value = packet.linearIssueBody;
    if (prProofOutput) prProofOutput.value = packet.prProofPacket;
    if (changeRequestPacketOutput) {
      changeRequestPacketOutput.value = JSON.stringify(packet.changerequest_handoff_packet, null, 2);
    }
    if (handoffStatus) {
      handoffStatus.textContent =
        `Prepared draft ChangeRequest handoff ${packet.changedModelHash}. No live Linear mutation was attempted.`;
    }
    setTimelineState("handoff");
    return packet;
  }

  function checksumEvidenceArchiveField(value) {
    return editableDraftHash(stableEvidenceArchiveJson(value));
  }

  function stableEvidenceArchiveJson(value) {
    return JSON.stringify(normalizeEvidenceArchiveValue(value));
  }

  function normalizeEvidenceArchiveValue(value) {
    if (value === undefined || typeof value === "function") return null;
    if (typeof value === "number" && !Number.isFinite(value)) return null;
    if (Array.isArray(value)) {
      return value.map((item) => normalizeEvidenceArchiveValue(item));
    }
    if (value && typeof value === "object") {
      return Object.keys(value)
        .sort()
        .reduce((accumulator, key) => {
          const normalized = normalizeEvidenceArchiveValue(value[key]);
          if (normalized !== undefined) accumulator[key] = normalized;
          return accumulator;
        }, {});
    }
    return value;
  }

  const foundationReviewArchiveKind = "well-harness-workbench-foundation-review-archive";
  const foundationReviewArchiveVersion = "workbench-foundation-review-archive.v1";
  const foundationReviewArchiveValidationKind =
    "well-harness-workbench-foundation-review-archive-validation-report";
  const foundationReviewArchiveValidationVersion =
    "workbench-foundation-review-archive-validation.v1";
  const foundationReviewArchiveSectionSpec = [
    ["workspace_document", "workspace_document_checksum"],
    ["editable_graph_document", "editable_graph_document_checksum"],
    ["model_json", "model_json_checksum"],
    ["diff_summary", "diff_summary_checksum"],
    ["candidate_baseline_diff_review_v2", "candidate_baseline_diff_review_v2_checksum"],
    ["sandbox_test_bench", "sandbox_test_bench_checksum"],
    ["sandbox_test_run_report", "sandbox_test_run_report_checksum"],
    ["candidate_debugger_view", "candidate_debugger_view_checksum"],
    ["preflight_analyzer_report", "preflight_analyzer_report_checksum"],
    ["hardware_bindings", "hardware_bindings_checksum"],
    ["hardware_evidence_v2", "hardware_evidence_v2_checksum"],
    ["interface_matrix", "interface_matrix_checksum"],
    ["connector_pin_map", "connector_pin_map_checksum"],
    ["hardware_interface_designer", "hardware_interface_designer_checksum"],
    ["hardware_interface_designer_validation", "hardware_interface_designer_validation_checksum"],
    ["changerequest_body", "changerequest_body_checksum"],
    ["pr_proof_packet", "pr_proof_packet_checksum"],
    ["changerequest_proof_packet", "changerequest_proof_packet_checksum"],
    ["changerequest_handoff_packet", "changerequest_handoff_packet_checksum"],
    ["gate_claims", "gate_claims_checksum"],
    ["known_blockers", "known_blockers_checksum"],
    ["red_line_metadata", "red_line_metadata_checksum"],
  ];

  function foundationReviewArchiveSection(archiveCore, checksums, key, checksumKey) {
    const value = archiveCore[key];
    const present = value !== undefined && value !== null;
    return {
      key,
      status: present ? "present" : "missing",
      kind: present && value && typeof value === "object" && !Array.isArray(value)
        ? String(value.kind || "untyped")
        : "untyped",
      version: present && value && typeof value === "object" && !Array.isArray(value)
        ? String(value.version || "unversioned")
        : "unversioned",
      checksum_key: checksumKey,
      checksum: checksums[checksumKey] || "missing",
      truth_effect: "none",
    };
  }

  function buildFoundationReviewArchiveBundle(archiveCore, checksums) {
    const sections = {};
    for (const [key, checksumKey] of foundationReviewArchiveSectionSpec) {
      sections[key] = foundationReviewArchiveSection(archiveCore, checksums, key, checksumKey);
    }
    const missingSections = Object.values(sections)
      .filter((section) => section.status !== "present")
      .map((section) => section.key);
    const preflight = archiveCore.preflight_analyzer_report || {};
    const handoff = archiveCore.changerequest_handoff_packet || {};
    return {
      kind: foundationReviewArchiveKind,
      version: foundationReviewArchiveVersion,
      review_scope: "workbench_v4_single_user_foundation",
      archive_kind: archiveCore.kind || "well-harness-workbench-evidence-archive",
      archive_version: archiveCore.version || 1,
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_level_impact: "none",
      dal_pssa_impact: "none",
      controller_truth_modified: false,
      frozen_assets_modified: false,
      live_linear_mutation: false,
      runtime_truth_effect: "none",
      truth_effect: "none",
      required_sections: foundationReviewArchiveSectionSpec.map(([key]) => key),
      missing_sections: missingSections,
      section_count: Object.keys(sections).length,
      sections,
      review_readiness: preflight.classification || "needs_evidence",
      preflight_summary: {
        classification: preflight.classification || "needs_evidence",
        finding_count: preflight.finding_count || 0,
        candidate_model_hash: preflight.candidate_model_hash || "unavailable",
        truth_effect: "none",
      },
      review_packet: {
        graph_checksum: checksums.editable_graph_document_checksum || "missing",
        test_bench_checksum: checksums.sandbox_test_bench_checksum || "missing",
        run_report_checksum: checksums.sandbox_test_run_report_checksum || "missing",
        debugger_checksum: checksums.candidate_debugger_view_checksum || "missing",
        preflight_checksum: checksums.preflight_analyzer_report_checksum || "missing",
        hardware_evidence_checksum: checksums.hardware_evidence_v2_checksum || "missing",
        changerequest_handoff_checksum: checksums.changerequest_handoff_packet_checksum || "missing",
        linear_issue_body_checksum: checksums.changerequest_body_checksum || "missing",
        pr_proof_packet_checksum: checksums.pr_proof_packet_checksum || "missing",
        truth_effect: "none",
      },
      linear_ready: {
        issue_body_available: Boolean(archiveCore.changerequest_body),
        pr_proof_available: Boolean(archiveCore.pr_proof_packet),
        handoff_packet_available: Boolean(handoff && handoff.kind),
        live_linear_mutation: false,
        browser_mutates_linear: false,
        truth_effect: "none",
      },
      restore_contract: {
        validation_report_key: "foundation_review_archive_validation",
        restore_payload_key: "foundation_review_archive_validation",
        requires_handoff_packet_validation: true,
        browser_archive_only: true,
        truth_effect: "none",
      },
      checksum_manifest: { ...checksums },
    };
  }

  function validateFoundationReviewArchiveBundle(bundle) {
    const findings = [];
    function addFinding(code, severity, message, path) {
      findings.push({
        code,
        severity,
        message,
        path,
        candidate_state: "sandbox_candidate",
        certification_claim: "none",
        truth_effect: "none",
      });
    }
    if (!bundle || typeof bundle !== "object" || Array.isArray(bundle)) {
      addFinding(
        "foundation_review_archive_invalid",
        "error",
        "foundation review archive must be an object",
        "foundation_review_archive",
      );
    } else {
      if (bundle.kind !== foundationReviewArchiveKind) {
        addFinding(
          "foundation_review_archive_invalid",
          "error",
          "foundation review archive kind must be well-harness-workbench-foundation-review-archive",
          "foundation_review_archive.kind",
        );
      }
      if (bundle.version !== foundationReviewArchiveVersion) {
        addFinding(
          "foundation_review_archive_invalid",
          "error",
          "foundation review archive version must be workbench-foundation-review-archive.v1",
          "foundation_review_archive.version",
        );
      }
      if (bundle.truth_effect !== "none") {
        addFinding(
          "foundation_review_archive_truth_boundary",
          "error",
          "foundation review archive truth_effect must be none",
          "foundation_review_archive.truth_effect",
        );
      }
      if (bundle.certification_claim !== "none") {
        addFinding(
          "foundation_review_archive_truth_boundary",
          "error",
          "foundation review archive certification_claim must be none",
          "foundation_review_archive.certification_claim",
        );
      }
      if (bundle.live_linear_mutation !== false) {
        addFinding(
          "foundation_review_archive_live_mutation",
          "error",
          "foundation review archive live_linear_mutation must be false",
          "foundation_review_archive.live_linear_mutation",
        );
      }
      const sections = bundle.sections || {};
      for (const [key, checksumKey] of foundationReviewArchiveSectionSpec) {
        const section = sections[key];
        if (!section || section.status !== "present") {
          addFinding(
            "foundation_review_archive_missing_section",
            "error",
            `Foundation review archive is missing required section ${key}.`,
            `foundation_review_archive.sections.${key}`,
          );
        }
        if (!section || !section.checksum || section.checksum === "missing") {
          addFinding(
            "foundation_review_archive_missing_checksum",
            "error",
            `Foundation review archive section ${key} is missing checksum ${checksumKey}.`,
            `foundation_review_archive.sections.${key}.checksum`,
          );
        }
      }
      if (!bundle.linear_ready || bundle.linear_ready.live_linear_mutation !== false) {
        addFinding(
          "foundation_review_archive_live_mutation",
          "error",
          "Foundation review archive linear_ready.live_linear_mutation must be false.",
          "foundation_review_archive.linear_ready.live_linear_mutation",
        );
      }
      if (!bundle.review_packet || bundle.review_packet.truth_effect !== "none") {
        addFinding(
          "foundation_review_archive_review_packet",
          "error",
          "Foundation review archive review_packet.truth_effect must be none.",
          "foundation_review_archive.review_packet.truth_effect",
        );
      }
      if (!bundle.restore_contract || bundle.restore_contract.truth_effect !== "none") {
        addFinding(
          "foundation_review_archive_restore_contract",
          "error",
          "Foundation review archive restore_contract.truth_effect must be none.",
          "foundation_review_archive.restore_contract.truth_effect",
        );
      }
    }
    const hasError = findings.some((finding) => finding.severity === "error");
    return {
      kind: foundationReviewArchiveValidationKind,
      version: foundationReviewArchiveValidationVersion,
      status: hasError ? "fail" : "pass",
      finding_count: findings.length,
      error_count: findings.filter((finding) => finding.severity === "error").length,
      findings,
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      truth_effect: "none",
    };
  }

  function buildWorkbenchEvidenceArchive() {
    const modelJson = buildEditableDraftExport();
    const workspaceDocument =
      modelJson.workspace_document || currentWorkspaceDocument();
    const canvasInteractionSummary =
      modelJson.canvas_interaction_summary || currentCanvasInteractionSummary();
    const editableGraphDocument =
      modelJson.editable_graph_document || buildEditableGraphDocumentFromSnapshot(modelJson);
    const hardwareBindings = collectWorkbenchHardwareBindings();
    const bindingCoverage = buildInterfaceBindingCoverageSummary(hardwareBindings);
    const hardwareBindingDiagnostics =
      modelJson.hardware_binding_diagnostics || buildHardwareBindingDiagnosticsReport(hardwareBindings);
    const interfaceMatrix =
      modelJson.interface_matrix || buildWorkbenchInterfaceMatrix(
        hardwareBindings,
        modelJson.typed_ports || [],
        hardwareBindingDiagnostics,
        bindingCoverage,
      );
    const interfaceMatrixValidation =
      modelJson.interface_matrix_validation || lastInterfaceMatrixValidationReport || null;
    const connectorPinMap =
      modelJson.connector_pin_map || buildWorkbenchConnectorPinMap(hardwareBindings);
    const hardwareInterfaceDesigner =
      modelJson.hardware_interface_designer || currentHardwareInterfaceDesignerPayload("archive");
    const hardwareInterfaceDesignerValidation =
      modelJson.hardware_interface_designer_validation
      || currentHardwareInterfaceDesignerValidationReport("archive");
    const hardwareEvidenceV2 =
      modelJson.hardware_evidence_v2 || currentHardwareEvidenceV2Report();
    const selectedDebugTimeline =
      modelJson.selected_debug_timeline || currentSelectedDebugTimelinePacket("archive");
    const candidateBaselineDiffReviewV2 =
      modelJson.candidate_baseline_diff_review_v2
      || currentCandidateBaselineDiffReviewV2Report("archive", modelJson.changed_model_hash);
    const sandboxTestBench =
      modelJson.sandbox_test_bench || safeSandboxTestBenchDefinition();
    const sandboxTestRunReport =
      modelJson.sandbox_test_run_report || currentSandboxTestRunReport();
    const candidateDebuggerView =
      modelJson.candidate_debugger_view || currentCandidateDebuggerView("archive");
    const preflightAnalyzerReport =
      modelJson.preflight_analyzer_report || currentPreflightAnalyzerReport("archive");
    const diagnosticFocus = modelJson.diagnostic_focus || currentDiagnosticFocusSummary();
    const diagnosticRepairActions = modelJson.repair_action_log || repairActionLogSnapshot();
    const typedPorts = modelJson.typed_ports || [];
    const portContractSummary =
      modelJson.port_contract_summary || buildPortContractSummary(typedPorts, modelJson.edges || []);
    const portCompatibilityReport =
      modelJson.port_compatibility_report || buildPortCompatibilityReport(typedPorts, modelJson.edges || []);
    const operationCatalog = modelJson.operation_catalog || buildOperationCatalogSummary();
    const componentLibrary = modelJson.component_library || buildComponentLibrarySummary();
    const subsystemGroupSummary = modelJson.subsystem_groups || subsystemGroupsSnapshot();
    const subsystemInterfaceContracts =
      modelJson.subsystem_interface_contracts || buildSubsystemInterfaceContractsSummary(subsystemGroupSummary);
    const ruleParameterSummary = modelJson.rule_parameter_summary || buildRuleParameterSummary();
    const hardwarePalette = modelJson.hardware_palette || buildHardwarePaletteSummary();
    const draftSnapshotManifest =
      modelJson.draft_snapshot_manifest || buildDraftSnapshotManifestSummary();
    const diffSummary = lastSandboxDiff || {
      verdict: "not_run",
      scenario_id: selectedWorkbenchScenarioId(),
      missing_diff_fallback: true,
      message: "Run sandbox before using this archive as review evidence.",
      truth_level_impact: "none",
    };
    const scenarioMetadata =
      (lastSandboxDiff && lastSandboxDiff.scenario_metadata) || currentWorkbenchScenarioMetadata();
    const handoffPacket = buildEditableHandoffPacket();
    const changeRequestProofPacket =
      modelJson.changerequest_proof_packet || handoffPacket.changerequest_proof_packet;
    const changeRequestHandoffPacket =
      modelJson.changerequest_handoff_packet || handoffPacket.changerequest_handoff_packet;
    const redLineMetadata = {
      red_lines_touched: "none",
      truth_level_impact: "none",
      dal_pssa_impact: "none",
      controller_truth_modified: false,
      frozen_assets_modified: false,
      live_linear_mutation: false,
    };
    const archiveCore = {
      kind: "well-harness-workbench-evidence-archive",
      version: 1,
      archive_scope: "local_draft_download",
      generated_at: "browser_local_draft",
      canvas_authoring_mode: modelJson.canvas_authoring_mode || canvasAuthoringMode,
      model_json: modelJson,
      workspace_document: workspaceDocument,
      canvas_interaction_summary: canvasInteractionSummary,
      editable_graph_document: editableGraphDocument,
      diff_summary: diffSummary,
      scenario_metadata: scenarioMetadata,
      hardware_bindings: hardwareBindings,
      binding_coverage: bindingCoverage,
      hardware_binding_diagnostics: hardwareBindingDiagnostics,
      interface_matrix: interfaceMatrix,
      interface_matrix_validation: interfaceMatrixValidation,
      connector_pin_map: connectorPinMap,
      hardware_interface_designer: hardwareInterfaceDesigner,
      hardware_interface_designer_validation: hardwareInterfaceDesignerValidation,
      hardware_evidence_v2: hardwareEvidenceV2,
      selected_debug_timeline: selectedDebugTimeline,
      candidate_baseline_diff_review_v2: candidateBaselineDiffReviewV2,
      sandbox_test_bench: sandboxTestBench,
      sandbox_test_run_report: sandboxTestRunReport,
      candidate_debugger_view: candidateDebuggerView,
      preflight_analyzer_report: preflightAnalyzerReport,
      diagnostic_focus: diagnosticFocus,
      repair_action_log: diagnosticRepairActions,
      typed_ports: typedPorts,
      port_contract_summary: portContractSummary,
      port_compatibility_report: portCompatibilityReport,
      operation_catalog: operationCatalog,
      component_library: componentLibrary,
      subsystem_groups: subsystemGroupSummary,
      subsystem_interface_contracts: subsystemInterfaceContracts,
      rule_parameter_summary: ruleParameterSummary,
      hardware_palette: hardwarePalette,
      draft_snapshot_manifest: draftSnapshotManifest,
      changerequest_proof_packet: changeRequestProofPacket,
      changerequest_handoff_packet: changeRequestHandoffPacket,
      selected_focus: changeRequestProofPacket.selected_focus,
      repair_action_log_summary: changeRequestProofPacket.repair_action_log_summary,
      changerequest_body: handoffPacket.linearIssueBody,
      pr_proof_packet: handoffPacket.prProofPacket,
      gate_claims: handoffPacket.gateClaims,
      known_blockers: handoffPacket.knownBlockers,
      red_line_metadata: redLineMetadata,
    };
    const checksums = {
      model_json_checksum: checksumEvidenceArchiveField(modelJson),
      workspace_document_checksum: checksumEvidenceArchiveField(workspaceDocument),
      canvas_interaction_summary_checksum: checksumEvidenceArchiveField(canvasInteractionSummary),
      editable_graph_document_checksum: checksumEvidenceArchiveField(editableGraphDocument),
      diff_summary_checksum: checksumEvidenceArchiveField(diffSummary),
      changerequest_proof_packet_checksum: checksumEvidenceArchiveField(changeRequestProofPacket),
      changerequest_handoff_packet_checksum: checksumEvidenceArchiveField(changeRequestHandoffPacket),
      selected_focus_checksum: checksumEvidenceArchiveField(changeRequestProofPacket.selected_focus),
      repair_action_log_summary_checksum: checksumEvidenceArchiveField(changeRequestProofPacket.repair_action_log_summary),
      changerequest_body_checksum: checksumEvidenceArchiveField(handoffPacket.linearIssueBody),
      pr_proof_packet_checksum: checksumEvidenceArchiveField(handoffPacket.prProofPacket),
      hardware_bindings_checksum: checksumEvidenceArchiveField(hardwareBindings),
      binding_coverage_checksum: checksumEvidenceArchiveField(bindingCoverage),
      hardware_binding_diagnostics_checksum: checksumEvidenceArchiveField(hardwareBindingDiagnostics),
      interface_matrix_checksum: checksumEvidenceArchiveField(interfaceMatrix),
      interface_matrix_validation_checksum: checksumEvidenceArchiveField(interfaceMatrixValidation),
      connector_pin_map_checksum: checksumEvidenceArchiveField(connectorPinMap),
      hardware_interface_designer_checksum: checksumEvidenceArchiveField(hardwareInterfaceDesigner),
      hardware_interface_designer_validation_checksum: checksumEvidenceArchiveField(hardwareInterfaceDesignerValidation),
      hardware_evidence_v2_checksum: checksumEvidenceArchiveField(hardwareEvidenceV2),
      selected_debug_timeline_checksum: checksumEvidenceArchiveField(selectedDebugTimeline),
      candidate_baseline_diff_review_v2_checksum: checksumEvidenceArchiveField(candidateBaselineDiffReviewV2),
      sandbox_test_bench_checksum: checksumEvidenceArchiveField(sandboxTestBench),
      sandbox_test_run_report_checksum: checksumEvidenceArchiveField(sandboxTestRunReport),
      candidate_debugger_view_checksum: checksumEvidenceArchiveField(candidateDebuggerView),
      preflight_analyzer_report_checksum: checksumEvidenceArchiveField(preflightAnalyzerReport),
      diagnostic_focus_checksum: checksumEvidenceArchiveField(diagnosticFocus),
      repair_action_log_checksum: checksumEvidenceArchiveField(diagnosticRepairActions),
      typed_ports_checksum: checksumEvidenceArchiveField(typedPorts),
      port_contract_summary_checksum: checksumEvidenceArchiveField(portContractSummary),
      port_compatibility_report_checksum: checksumEvidenceArchiveField(portCompatibilityReport),
      operation_catalog_checksum: checksumEvidenceArchiveField(operationCatalog),
      component_library_checksum: checksumEvidenceArchiveField(componentLibrary),
      subsystem_groups_checksum: checksumEvidenceArchiveField(subsystemGroupSummary),
      subsystem_interface_contracts_checksum: checksumEvidenceArchiveField(subsystemInterfaceContracts),
      rule_parameter_summary_checksum: checksumEvidenceArchiveField(ruleParameterSummary),
      hardware_palette_checksum: checksumEvidenceArchiveField(hardwarePalette),
      draft_snapshot_manifest_checksum: checksumEvidenceArchiveField(draftSnapshotManifest),
      gate_claims_checksum: checksumEvidenceArchiveField(handoffPacket.gateClaims),
      known_blockers_checksum: checksumEvidenceArchiveField(handoffPacket.knownBlockers),
      red_line_metadata_checksum: checksumEvidenceArchiveField(redLineMetadata),
    };
    const foundationReviewArchive = buildFoundationReviewArchiveBundle(archiveCore, checksums);
    const foundationReviewArchiveValidation =
      validateFoundationReviewArchiveBundle(foundationReviewArchive);
    const finalArchiveCore = {
      ...archiveCore,
      foundation_review_archive: foundationReviewArchive,
      foundation_review_archive_validation: foundationReviewArchiveValidation,
    };
    const finalChecksums = {
      ...checksums,
      foundation_review_archive_checksum: checksumEvidenceArchiveField(foundationReviewArchive),
      foundation_review_archive_validation_checksum: checksumEvidenceArchiveField(foundationReviewArchiveValidation),
    };
    return {
      ...finalArchiveCore,
      checksums: {
        ...finalChecksums,
        manifest_checksum: checksumEvidenceArchiveField({
          archiveCore: finalArchiveCore,
          checksums: finalChecksums,
        }),
      },
    };
  }

  function renderWorkbenchEvidenceArchive() {
    const archive = buildWorkbenchEvidenceArchive();
    if (archiveOutput) archiveOutput.value = JSON.stringify(archive, null, 2);
    if (archiveStatus) {
      archiveStatus.textContent =
        `Prepared local draft archive ${archive.checksums.manifest_checksum}. No live Linear mutation.`;
    }
    setTimelineState("handoff");
    return archive;
  }

  function downloadWorkbenchEvidenceArchive() {
    const archive = archiveOutput && archiveOutput.value
      ? JSON.parse(archiveOutput.value)
      : renderWorkbenchEvidenceArchive();
    if (typeof Blob === "undefined" || typeof URL === "undefined" || !document.body) {
      if (archiveStatus) {
        archiveStatus.textContent = "Archive JSON prepared locally; browser download API unavailable.";
      }
      return archive;
    }
    const blob = new Blob([JSON.stringify(archive, null, 2)], { type: "application/json" });
    const href = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = href;
    anchor.download = "workbench-evidence-archive-draft.json";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(href);
    if (archiveStatus) {
      archiveStatus.textContent =
        `Downloaded local draft archive ${archive.checksums.manifest_checksum}. No live Linear mutation.`;
    }
    return archive;
  }

  function attachEditableNodeHandler(node) {
    if (!node || node.getAttribute("data-node-handler-attached") === "true") return;
    node.setAttribute("data-node-handler-attached", "true");
    node.addEventListener("pointerdown", (event) => {
      beginEditableGroupDrag(event, node);
    });
    node.addEventListener("pointermove", (event) => {
      updateEditableGroupDrag(event);
    });
    node.addEventListener("pointerup", (event) => {
      endEditableGroupDrag(event);
    });
    node.addEventListener("pointercancel", (event) => {
      endEditableGroupDrag(event);
    });
    node.addEventListener("click", (event) => {
      if (suppressNextNodeClick) {
        event.preventDefault();
        event.stopPropagation();
        suppressNextNodeClick = false;
        return;
      }
      selectNode(node, { multiSelect: isSelectionModifier(event) });
    });
  }

  if (canvas) {
    canvas.addEventListener("pointerdown", (event) => beginEditableGroupDragFromEventTarget(event), true);
    canvas.addEventListener("pointerdown", (event) => beginCanvasLasso(event));
    canvas.addEventListener("pointermove", (event) => {
      if (groupDragState) {
        updateEditableGroupDrag(event);
        return;
      }
      updateCanvasLasso(event);
    });
    canvas.addEventListener("pointerup", (event) => {
      if (groupDragState) {
        endEditableGroupDrag(event);
        return;
      }
      endCanvasLasso(event);
    });
    canvas.addEventListener("pointercancel", (event) => {
      if (groupDragState) {
        endEditableGroupDrag(event);
        return;
      }
      endCanvasLasso(event);
    });
    window.addEventListener("pointermove", (event) => {
      if (groupDragState) updateEditableGroupDrag(event);
    });
    window.addEventListener("pointerup", (event) => {
      if (groupDragState) endEditableGroupDrag(event);
    });
    window.addEventListener("pointercancel", (event) => {
      if (groupDragState) endEditableGroupDrag(event);
    });
    window.addEventListener("pointerdown", (event) => beginEditableGroupDragFromEventTarget(event), true);
  }

  restoreDraft();
  for (const node of nodes) {
    attachEditableNodeHandler(node);
  }
  if (deriveBtn) {
    deriveBtn.addEventListener("click", () => deriveDraft());
  }
  if (runSandboxBtn) {
    runSandboxBtn.addEventListener("click", () => runWorkbenchSandboxDiff());
  }
  if (runTestBenchBtn) {
    runTestBenchBtn.addEventListener("click", () => runSandboxTestBench());
  }
  if (runPreflightBtn) {
    runPreflightBtn.addEventListener("click", () => runWorkbenchPreflightAnalyzer());
  }
  if (startEmptyDraftBtn) {
    startEmptyDraftBtn.addEventListener("click", () => startEmptyCanvasDraft());
  }
  for (const button of toolbarButtons) {
    button.addEventListener("click", () => {
      const tool = button.getAttribute("data-editor-tool") || "select";
      if (tool === "node") {
        setEditorTool("node");
        addEditableNode();
        setEditorTool("select");
      } else if (tool === "duplicate") {
        duplicateSelectedEditableNode();
        setEditorTool("select");
      } else if (tool === "group") {
        groupSelectedDraftNodes();
        setEditorTool("select");
      } else if (tool === "ungroup") {
        ungroupSelectedSubsystem();
        setEditorTool("select");
      } else if (tool === "edge") {
        setEditorTool("edge");
        beginEditableEdgeConnect();
      } else if (tool === "remove") {
        removeSelectedEditableNode();
        setEditorTool("select");
      } else if (tool === "disconnect") {
        disconnectSelectedEditableEdge();
        setEditorTool("select");
      } else if (tool === "undo") {
        undoEditableEdit();
        setEditorTool("select");
      } else if (tool === "redo") {
        redoEditableEdit();
        setEditorTool("select");
      } else {
        pendingEdgeSourceId = "";
        setEditorTool("select");
      }
    });
  }
  for (const button of viewportButtons) {
    button.addEventListener("click", () => {
      const tool = button.getAttribute("data-viewport-tool") || "reset";
      if (tool === "zoom-in") {
        zoomViewportAt(1.18, null, "zoom in");
      } else if (tool === "zoom-out") {
        zoomViewportAt(1 / 1.18, null, "zoom out");
      } else if (tool === "fit-selection") {
        fitViewportToSelection();
      } else {
        resetViewport();
      }
    });
  }
  if (canvas) {
    canvas.addEventListener("wheel", (event) => {
      if (!event.ctrlKey && !event.metaKey) return;
      const anchor = canvasViewportPoint(event);
      const factor = event.deltaY < 0 ? 1.12 : 1 / 1.12;
      event.preventDefault();
      zoomViewportAt(factor, anchor, "wheel zoom");
    }, { passive: false });
  }
  for (const button of opCatalogButtons) {
    button.addEventListener("click", () => {
      const op = button.getAttribute("data-op-catalog-op") || "and";
      setSelectedOperationCatalogEntry(op);
      if (draftLabel) {
        draftLabel.textContent = `sandbox_candidate op catalog selected: ${selectedCatalogOp}`;
      }
      persistDraft();
    });
  }
  for (const button of componentLibraryButtons) {
    button.addEventListener("click", () => {
      const templateId = button.getAttribute("data-component-template-id") || "";
      instantiateComponentTemplate(templateId);
      setEditorTool("select");
    });
  }
  if (captureSubsystemTemplateBtn) {
    captureSubsystemTemplateBtn.addEventListener("click", () => {
      captureSelectedSubsystemTemplate();
      setEditorTool("select");
    });
  }
  if (insertCapturedTemplateBtn) {
    insertCapturedTemplateBtn.addEventListener("click", () => {
      insertLatestCapturedSubsystemTemplate();
      setEditorTool("select");
    });
  }
  if (createSubsystemBtn) {
    createSubsystemBtn.addEventListener("click", () => groupSelectedDraftNodes());
  }
  if (renameSubsystemBtn) {
    renameSubsystemBtn.addEventListener("click", () => renameSelectedSubsystemGroup());
  }
  if (ungroupSubsystemBtn) {
    ungroupSubsystemBtn.addEventListener("click", () => ungroupSelectedSubsystem());
  }
  if (addSubsystemInterfacePortBtn) {
    addSubsystemInterfacePortBtn.addEventListener("click", () => addSubsystemInterfaceContractPort());
  }
  if (removeSubsystemInterfacePortBtn) {
    removeSubsystemInterfacePortBtn.addEventListener("click", () => removeSubsystemInterfaceContractPort());
  }
  if (labelInput) {
    labelInput.addEventListener("input", () => {
      if (!selectedNode) return;
      if (labelInput.getAttribute("data-edit-history-open") !== "true") {
        recordEditableHistory("label_edit");
        labelInput.setAttribute("data-edit-history-open", "true");
      }
      selectedNode.setAttribute("data-node-label", labelInput.value);
      const small = selectedNode.querySelector("small");
      if (small) {
        small.textContent = `${(opSelect && opSelect.value) || "and"} · draft`;
      }
      if (draftLabel) draftLabel.textContent = "sandbox_candidate label edit pending";
      validateEditableGraph();
      updateEditableDraftHash();
      persistDraft();
    });
    labelInput.addEventListener("change", () => {
      labelInput.removeAttribute("data-edit-history-open");
    });
  }
  if (opSelect) {
    opSelect.addEventListener("change", () => {
      if (!selectedNode) return;
      recordEditableHistory("op_edit");
      selectedNode.setAttribute("data-node-op", opSelect.value);
      selectedNode.setAttribute("data-op-catalog-entry", operationCatalogEntry(opSelect.value).op);
      const small = selectedNode.querySelector("small");
      if (small) {
        small.textContent = `${opSelect.value} · ${selectedNode.getAttribute("data-rule-count") || "0"} rules`;
      }
      if (draftLabel) draftLabel.textContent = "sandbox_candidate op edit pending";
      validateEditableGraph();
      updateEditableDraftHash();
      persistDraft();
    });
  }
  if (handoffBtn) {
    handoffBtn.addEventListener("click", () => renderEditableHandoffPacket());
  }
  if (prepareArchiveBtn) {
    prepareArchiveBtn.addEventListener("click", () => renderWorkbenchEvidenceArchive());
  }
  if (downloadArchiveBtn) {
    downloadArchiveBtn.addEventListener("click", () => downloadWorkbenchEvidenceArchive());
  }
  if (sandboxTestBenchInputs) {
    sandboxTestBenchInputs.addEventListener("input", () => {
      lastSandboxTestRunReport = null;
      lastPreflightAnalyzerReport = null;
      if (sandboxTestBenchStatus) sandboxTestBenchStatus.textContent = "edited";
      if (sandboxTestBenchPanel) sandboxTestBenchPanel.setAttribute("data-test-status", "edited");
      renderWorkbenchPreflightAnalyzerReport(currentPreflightAnalyzerReport("test_bench_edited"));
      persistDraft();
    });
  }
  if (sandboxTestBenchAssertions) {
    sandboxTestBenchAssertions.addEventListener("input", () => {
      lastSandboxTestRunReport = null;
      lastPreflightAnalyzerReport = null;
      if (sandboxTestBenchStatus) sandboxTestBenchStatus.textContent = "edited";
      if (sandboxTestBenchPanel) sandboxTestBenchPanel.setAttribute("data-test-status", "edited");
      renderWorkbenchPreflightAnalyzerReport(currentPreflightAnalyzerReport("test_bench_edited"));
      persistDraft();
    });
  }

  function isFormShortcutTarget(target) {
    if (!(target instanceof HTMLElement)) return false;
    return Boolean(target.closest("input, textarea, select, [contenteditable='true']"));
  }

  function releaseSpacePanMode() {
    spacePanActive = false;
    if (canvas) canvas.removeAttribute("data-space-pan-active");
  }

  function cancelViewportPanMode() {
    if (!viewportPanState) return;
    clearViewportPanState("pan cancelled");
  }

  function handleEditableKeyboardShortcut(event) {
    if (!event || isFormShortcutTarget(event.target)) return;
    const key = String(event.key || "").toLowerCase();
    const commandKey = event.metaKey || event.ctrlKey;
    if (event.code === "Space" || event.key === " ") {
      spacePanActive = true;
      if (canvas) canvas.setAttribute("data-space-pan-active", "true");
      event.preventDefault();
      return;
    }
    if (commandKey && key === "d") {
      event.preventDefault();
      duplicateSelectedEditableNode();
      return;
    }
    if (commandKey && key === "g") {
      event.preventDefault();
      if (event.shiftKey) {
        ungroupSelectedSubsystem();
      } else {
        groupSelectedDraftNodes();
      }
      return;
    }
    if (commandKey && key === "z") {
      event.preventDefault();
      if (event.shiftKey) {
        redoEditableEdit();
      } else {
        undoEditableEdit();
      }
      return;
    }
    if (event.ctrlKey && key === "y") {
      event.preventDefault();
      redoEditableEdit();
      return;
    }
    if (!commandKey && (event.key === "Delete" || event.key === "Backspace")) {
      event.preventDefault();
      if (selectedEdge) {
        disconnectSelectedEditableEdge();
      } else {
        removeSelectedEditableNode();
      }
      return;
    }
    if (event.key === "Escape" && pendingEdgeSourceId) {
      event.preventDefault();
      pendingEdgeSourceId = "";
      setEditorTool("select");
      if (graphValidationStatus) {
        graphValidationStatus.textContent = "Graph validation: edge connection cancelled.";
      }
    }
  }

  document.addEventListener("keydown", handleEditableKeyboardShortcut);
  document.addEventListener("keyup", (event) => {
    if (event && (event.code === "Space" || event.key === " ")) {
      releaseSpacePanMode();
    }
  });
  window.addEventListener("blur", () => {
    releaseSpacePanMode();
    cancelViewportPanMode();
  });
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") {
      releaseSpacePanMode();
      cancelViewportPanMode();
    }
  });
  if (hardwarePaletteFilter) {
    hardwarePaletteFilter.addEventListener("change", () => renderHardwarePalette());
  }
  if (hardwarePaletteAction) {
    hardwarePaletteAction.addEventListener("change", () => {
      if (hardwarePaletteStatus) {
        hardwarePaletteStatus.textContent =
          `Palette click action: ${currentHardwarePaletteAction()}. Sandbox evidence only; truth effect: none.`;
      }
      renderHardwarePalette();
    });
  }
  if (hardwarePaletteList) {
    hardwarePaletteList.addEventListener("click", (event) => {
      const target = event.target instanceof Element
        ? event.target.closest("[data-hardware-palette-id]")
        : null;
      if (!target) return;
      event.preventDefault();
      handleHardwarePaletteItem(target.getAttribute("data-hardware-palette-id") || "");
    });
  }
  if (hardwareBindingDiagnosticsList) {
    hardwareBindingDiagnosticsList.addEventListener("click", handleHardwareBindingDiagnosticActivation);
    hardwareBindingDiagnosticsList.addEventListener("keydown", handleHardwareBindingDiagnosticActivation);
    hardwareBindingDiagnosticsList.addEventListener("click", handleHardwareBindingDiagnosticRepairActivation);
    hardwareBindingDiagnosticsList.addEventListener("keydown", handleHardwareBindingDiagnosticRepairActivation);
  }
  if (applyInterfaceBindingBtn) {
    applyInterfaceBindingBtn.addEventListener("click", () => applySelectedInterfaceBinding());
  }
  if (exportConnectorPinMapBtn) {
    exportConnectorPinMapBtn.addEventListener("click", () => exportWorkbenchConnectorPinMap());
  }
  if (applyConnectorPinMapBtn) {
    applyConnectorPinMapBtn.addEventListener("click", () => applyWorkbenchConnectorPinMap());
  }
  if (connectorPinMapOutput) {
    connectorPinMapOutput.addEventListener("input", () => {
      if (connectorPinMapStatus) {
        connectorPinMapStatus.textContent = "Connector/pin map edited; apply to update sandbox metadata. Truth effect: none.";
      }
    });
  }
  if (exportHardwareInterfaceDesignBtn) {
    exportHardwareInterfaceDesignBtn.addEventListener("click", () => exportHardwareInterfaceDesigner());
  }
  if (validateHardwareInterfaceDesignBtn) {
    validateHardwareInterfaceDesignBtn.addEventListener("click", () => validateHardwareInterfaceDesignerFromEditor());
  }
  if (applyHardwareInterfaceDesignBtn) {
    applyHardwareInterfaceDesignBtn.addEventListener("click", () => applyHardwareInterfaceDesignerFromEditor());
  }
  if (hardwareInterfaceDesignOutput) {
    hardwareInterfaceDesignOutput.addEventListener("input", () => {
      if (hardwareInterfaceDesignStatus) {
        hardwareInterfaceDesignStatus.textContent =
          "Hardware/interface design edited; validate before applying. Truth effect: none.";
      }
    });
  }
  if (applyRuleParameterBtn) {
    applyRuleParameterBtn.addEventListener("click", () => applySelectedRuleParameter());
  }
  if (applyPortContractBtn) {
    applyPortContractBtn.addEventListener("click", () => applySelectedPortContract());
  }
  if (exportInterfaceMatrixBtn) {
    exportInterfaceMatrixBtn.addEventListener("click", () => exportWorkbenchInterfaceMatrix());
  }
  if (exportInterfaceMatrixCsvBtn) {
    exportInterfaceMatrixCsvBtn.addEventListener("click", () => exportWorkbenchInterfaceMatrixCsv());
  }
  if (importInterfaceMatrixCsvBtn) {
    importInterfaceMatrixCsvBtn.addEventListener("click", () => importWorkbenchInterfaceMatrixCsv());
  }
  if (validateInterfaceMatrixBtn) {
    validateInterfaceMatrixBtn.addEventListener("click", () => validateWorkbenchInterfaceMatrix());
  }
  if (applyInterfaceMatrixBtn) {
    applyInterfaceMatrixBtn.addEventListener("click", () => applyWorkbenchInterfaceMatrix());
  }
  if (interfaceMatrixOutput) {
    interfaceMatrixOutput.addEventListener("input", () => {
      clearInterfaceMatrixValidationReport("Matrix edited; validate before apply. Truth effect: none.");
    });
  }
  if (interfaceMatrixCsvOutput) {
    interfaceMatrixCsvOutput.addEventListener("input", () => {
      clearInterfaceMatrixValidationReport("Spreadsheet matrix edited; import before apply. Truth effect: none.");
    });
  }
  if (exportDraftBtn) {
    exportDraftBtn.addEventListener("click", () => exportEditableDraftJson());
  }
  if (importDraftBtn) {
    importDraftBtn.addEventListener("click", () => importEditableDraftJson());
  }
  if (saveDraftSnapshotBtn) {
    saveDraftSnapshotBtn.addEventListener("click", () => saveNamedDraftSnapshot());
  }
  if (restoreDraftSnapshotBtn) {
    restoreDraftSnapshotBtn.addEventListener("click", () => restoreNamedDraftSnapshot());
  }
  if (deleteDraftSnapshotBtn) {
    deleteDraftSnapshotBtn.addEventListener("click", () => deleteNamedDraftSnapshot());
  }
  setSelectedOperationCatalogEntry(selectedCatalogOp);
  refreshCapturedSubsystemTemplateControls();
  renderDraftSnapshotManager();
  applyViewportTransform();
  if (selectedNode) {
    selectNode(selectedNode);
  }
  renderEditableEdges();
  validateEditableGraph();
  updateEditableDraftHash();
  renderCandidateDebuggerView(currentCandidateDebuggerView("init"));
  renderWorkbenchPreflightAnalyzerReport(currentPreflightAnalyzerReport("init"));
  renderHardwarePalette();
  hydrateEvidenceSummary();
}

if (typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", installEditableWorkbenchShell);
  } else {
    installEditableWorkbenchShell();
  }
}

// ─── P52-07: new-circuit creation flow ────────────────────────────
//
// Three template cards (radio-like behavior) + derive-from-current
// shortcut + name input + create button. Backend wiring is stubbed
// for this slice — submit shows a confirmation in the status span
// and closes the drawer after a short pause. A future phase can
// land the /api/circuits POST.
(function _wbNewCircuitBoot() {
  if (typeof document === "undefined") return;
  const drawer = document.getElementById("workbench-tool-new");
  if (!drawer) return;

  const fieldset = drawer.querySelector("#workbench-new-circuit-templates");
  const cards = fieldset
    ? Array.from(fieldset.querySelectorAll("[data-template-id]"))
    : [];
  const deriveBtn = drawer.querySelector('[data-circuit-action="derive-from-current"]');
  const nameInput = drawer.querySelector("#workbench-new-circuit-name");
  const createBtn = drawer.querySelector("#workbench-new-circuit-create-btn");
  const statusEl = drawer.querySelector("#workbench-new-circuit-status");

  function selectTemplate(targetId) {
    for (const card of cards) {
      const isActive = card.getAttribute("data-template-id") === targetId;
      card.setAttribute("data-template-selected", isActive ? "true" : "false");
      card.setAttribute("aria-pressed", isActive ? "true" : "false");
    }
  }

  for (const card of cards) {
    card.addEventListener("click", () => {
      const id = card.getAttribute("data-template-id");
      if (id) selectTemplate(id);
    });
  }

  if (deriveBtn) {
    deriveBtn.addEventListener("click", () => {
      // Treat derive as a fourth implicit selection — mark all
      // template cards as inactive and surface a status message.
      for (const card of cards) {
        card.setAttribute("data-template-selected", "false");
        card.setAttribute("aria-pressed", "false");
      }
      if (statusEl) {
        statusEl.textContent = "已选: 派生自当前电路 · derive from current selected";
        statusEl.setAttribute("data-status", "idle");
      }
    });
  }

  function selectedTemplateId() {
    const active = cards.find(
      (c) => c.getAttribute("data-template-selected") === "true"
    );
    return active ? active.getAttribute("data-template-id") : "derive-from-current";
  }

  if (createBtn) {
    createBtn.addEventListener("click", () => {
      const name = (nameInput && nameInput.value.trim()) || "未命名电路 · Untitled";
      const tplId = selectedTemplateId();
      if (statusEl) {
        statusEl.textContent =
          `已收到创建请求 · created (template=${tplId}, name="${name}")`;
        statusEl.setAttribute("data-status", "success");
      }
      // Auto-dismiss the drawer after a beat so the user sees the
      // confirmation but isn't left staring at a stale form.
      setTimeout(() => {
        document.body.dataset.activeTool = "";
        const dock = document.getElementById("workbench-dock");
        if (dock) {
          for (const btn of dock.querySelectorAll("[data-dock-target]")) {
            btn.setAttribute("aria-pressed", "false");
          }
        }
      }, 1200);
    });
  }
})();

/* FANTUI 反推逻辑演示舱 — slim demo.js.
 *
 * Architecture: stateless signal-level evaluation via /api/lever-snapshot.
 * User moves TRA slider / toggles → debounced POST → render chain SVG + HUD
 * + output cards + status banner. No state machine replay.
 *
 * Phase UI-D (2026-04-22): replaced legacy ~2100-line demo.js.
 * Legacy archived at archive/shelved/multi-system-ui/static/legacy-demo.js.
 */
(function () {
  "use strict";

  const API_URL = "/api/lever-snapshot";
  const DEBOUNCE_MS = 120;

  const $ = (id) => document.getElementById(id);

  const inputs = {
    tra:               $("fan-tra-lever"),
    ra:                $("fan-ra"),
    n1k:               $("fan-n1k"),
    vdt:               $("fan-vdt"),
    engineRunning:     $("fan-engine-running"),
    aircraftOnGround:  $("fan-aircraft-on-ground"),
    reverserInhibited: $("fan-reverser-inhibited"),
    eecEnable:         $("fan-eec-enable"),
    feedbackMode:      $("fan-feedback-mode"),
  };

  const readouts = {
    traValue:       $("fan-tra-value"),
    traZone:        $("fan-tra-zone"),
    raValue:        $("fan-ra-value"),
    n1kValue:       $("fan-n1k-value"),
    vdtValue:       $("fan-vdt-value"),
    statusBadge:    $("fan-status-badge"),
    statusSummary:  $("fan-status-summary"),
    completionFlag: $("fan-completion-flag"),
    hudSw1:         $("fan-hud-sw1"),
    hudSw2:         $("fan-hud-sw2"),
    hudTls:         $("fan-hud-tls"),
    hudVdt90:       $("fan-hud-vdt90"),
    hudLogic:       $("fan-hud-logic"),
    hudThrLock:     $("fan-hud-thr-lock"),
    outTls115:      $("fan-out-tls115"),
    outTls115V:     $("fan-out-tls115-value"),
    outEtrac:       $("fan-out-etrac"),
    outEtracV:      $("fan-out-etrac-value"),
    outEec:         $("fan-out-eec"),
    outEecV:        $("fan-out-eec-value"),
    outThr:         $("fan-out-thr"),
    outThrV:        $("fan-out-thr-value"),
    presetStatus:   $("fan-preset-status"),
  };

  const chainSvg = document.getElementById("fan-chain-svg");

  function numValue(el, fallback) {
    if (!el) return fallback;
    const v = parseFloat(el.value);
    return Number.isFinite(v) ? v : fallback;
  }
  function checked(el) { return !!(el && el.checked); }

  function buildRequest() {
    return {
      tra_deg:                  numValue(inputs.tra, 0),
      radio_altitude_ft:        numValue(inputs.ra, 0),
      n1k:                      numValue(inputs.n1k, 0.35) / 100,
      engine_running:           checked(inputs.engineRunning),
      aircraft_on_ground:       checked(inputs.aircraftOnGround),
      reverser_inhibited:       checked(inputs.reverserInhibited),
      eec_enable:               checked(inputs.eecEnable),
      feedback_mode:            inputs.feedbackMode ? inputs.feedbackMode.value : "auto_scrubber",
      deploy_position_percent:  numValue(inputs.vdt, 0),
    };
  }

  function zoneFromTra(tra) {
    if (tra <= -25) return ["rev-range", "MAX REV"];
    if (tra <= -13) return ["rev-range", "DEEP REV"];
    if (tra <= -9)  return ["rev-range", "REV"];
    if (tra < 0)    return ["rev-idle", "REV IDLE"];
    return ["fwd", "FWD"];
  }

  function formatBool(value) {
    if (value === true)  return "TRUE";
    if (value === false) return "false";
    return "—";
  }

  // ═══════════ Fetch pipeline ═══════════
  let pending = null;
  let inflight = false;
  let nextRequest = false;

  async function fetchEvaluation() {
    if (inflight) {
      nextRequest = true;
      return;
    }
    inflight = true;
    const payload = buildRequest();
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        console.warn("[demo] snapshot eval failed:", response.status);
        return;
      }
      const data = await response.json();
      renderAll(data, payload);
    } catch (err) {
      console.warn("[demo] fetch error:", err);
    } finally {
      inflight = false;
      if (nextRequest) {
        nextRequest = false;
        fetchEvaluation();
      }
    }
  }

  function scheduleFetch() {
    if (pending) clearTimeout(pending);
    pending = setTimeout(() => {
      pending = null;
      fetchEvaluation();
    }, DEBOUNCE_MS);
  }

  // ═══════════ Rendering ═══════════
  function renderAll(data, request) {
    const nodes = Array.isArray(data.nodes) ? data.nodes : [];
    const nodeById = new Map(nodes.map((n) => [n.id, n]));

    renderLeverHud(request);
    renderChain(nodeById);
    renderOutputs(nodeById);
    renderHud(nodeById);
    renderStatus(data, nodeById);
  }

  function renderLeverHud(req) {
    if (readouts.traValue) readouts.traValue.textContent = req.tra_deg.toFixed(1) + "°";
    if (readouts.traZone) {
      const [zone, label] = zoneFromTra(req.tra_deg);
      readouts.traZone.dataset.zone = zone;
      readouts.traZone.textContent = label;
    }
    if (readouts.raValue)  readouts.raValue.textContent  = req.radio_altitude_ft.toFixed(0) + " ft";
    if (readouts.n1kValue) readouts.n1kValue.textContent = (req.n1k * 100).toFixed(0) + "%";
    if (readouts.vdtValue) readouts.vdtValue.textContent = req.deploy_position_percent.toFixed(0) + "%";
  }

  function renderChain(nodeById) {
    if (!chainSvg) return;
    chainSvg.querySelectorAll(".chain-node, .chain-logic").forEach((group) => {
      const nodeId = group.getAttribute("data-node");
      const node = nodeById.get(nodeId);
      group.dataset.state = node ? (node.state || "idle") : "idle";
    });
  }

  function renderOutputs(nodeById) {
    setOutputCard(readouts.outTls115, readouts.outTls115V, nodeById.get("tls115"));
    setOutputCard(readouts.outEtrac,  readouts.outEtracV,  nodeById.get("etrac_540v"));
    setOutputCard(readouts.outEec,    readouts.outEecV,    nodeById.get("eec_deploy"));
    setOutputCard(readouts.outThr,    readouts.outThrV,    nodeById.get("thr_lock"));
  }

  function setOutputCard(card, valueEl, node) {
    if (!card || !valueEl) return;
    const state = node ? node.state : "idle";
    card.dataset.state = state === "active" ? "active" : (state === "blocked" ? "blocked" : "idle");
    valueEl.textContent = state === "active" ? "ON" : (state === "blocked" ? "BLOCKED" : "OFF");
  }

  function renderHud(nodeById) {
    const sw1 = nodeById.get("sw1");
    const sw2 = nodeById.get("sw2");
    if (readouts.hudSw1) {
      readouts.hudSw1.textContent = sw1 && sw1.state === "active" ? "CLOSED" : "open";
      readouts.hudSw1.dataset.flag = sw1 && sw1.state === "active" ? "true" : "false";
    }
    if (readouts.hudSw2) {
      readouts.hudSw2.textContent = sw2 && sw2.state === "active" ? "CLOSED" : "open";
      readouts.hudSw2.dataset.flag = sw2 && sw2.state === "active" ? "true" : "false";
    }
    const tls = nodeById.get("tls_unlocked");
    if (readouts.hudTls) {
      readouts.hudTls.textContent = tls && tls.state === "active" ? "UNLOCKED" : "locked";
      readouts.hudTls.dataset.flag = tls && tls.state === "active" ? "true" : "false";
    }
    const vdt90 = nodeById.get("vdt90");
    if (readouts.hudVdt90) {
      readouts.hudVdt90.textContent = vdt90 && vdt90.state === "active" ? "≥90%" : "pending";
      readouts.hudVdt90.dataset.flag = vdt90 && vdt90.state === "active" ? "true" : "false";
    }
    if (readouts.hudLogic) {
      const parts = ["logic1", "logic2", "logic3", "logic4"].map((id, i) => {
        const n = nodeById.get(id);
        const on = n && n.state === "active";
        return `L${i+1}:${on ? "ON" : "—"}`;
      });
      readouts.hudLogic.textContent = parts.join(" · ");
    }
    const thr = nodeById.get("thr_lock");
    if (readouts.hudThrLock) {
      if (thr && thr.state === "active") {
        readouts.hudThrLock.textContent = "RELEASED";
        readouts.hudThrLock.dataset.flag = "true";
      } else if (thr && thr.state === "blocked") {
        readouts.hudThrLock.textContent = "BLOCKED";
        readouts.hudThrLock.dataset.flag = "fault";
      } else {
        readouts.hudThrLock.textContent = "—";
        readouts.hudThrLock.dataset.flag = "false";
      }
    }
  }

  function renderStatus(data, nodeById) {
    const thr = nodeById.get("thr_lock");
    const logic4 = nodeById.get("logic4");
    const logic3 = nodeById.get("logic3");
    const inhibited = checked(inputs.reverserInhibited);

    let state = "idle";
    let summary = "等待拉杆快照 …";
    let reached = false;

    if (inhibited) {
      state = "fault";
      summary = "反推被抑制 (reverser_inhibited=TRUE)：所有 deploy 链路阻塞。";
    } else if (thr && thr.state === "active") {
      state = "deployed";
      summary = "L4 满足，THR_LOCK 释放。油门反向段解锁。";
      reached = true;
    } else if (logic4 && logic4.state === "blocked") {
      state = "fault";
      const blockers = (logic4.blockers || []).join(" / ") || "VDT90 / plant feedback";
      summary = `L4 阻塞：${blockers}。`;
    } else if (logic3 && logic3.state === "active") {
      state = "deploying";
      summary = "L3 激活：EEC deploy / PLS / PDU 通电。等待 VDT90 ≥ 90%。";
    } else if (nodeById.get("logic2") && nodeById.get("logic2").state === "active") {
      state = "ready";
      summary = "L2 激活：ETRAC 540VDC 已供电，等待 L3 条件。";
    } else if (nodeById.get("logic1") && nodeById.get("logic1").state === "active") {
      state = "ready";
      summary = "L1 激活：TLS 115VAC 已供电。等待 L2 条件（SW2 + engine_running + TLS 解锁）。";
    } else {
      state = "idle";
      summary = "等待输入：TRA 拉杆 / RA / aircraft_on_ground 未满足 L1 前置条件。";
    }

    if (readouts.statusBadge) {
      readouts.statusBadge.dataset.state = state;
      readouts.statusBadge.textContent = ({
        idle: "IDLE", ready: "READY", deploying: "DEPLOYING",
        deployed: "DEPLOYED", stowing: "STOWING", fault: "FAULT",
      })[state] || "IDLE";
    }
    if (readouts.statusSummary) readouts.statusSummary.textContent = summary;
    if (readouts.completionFlag) {
      readouts.completionFlag.textContent = reached ? "已达成" : "未达成";
      readouts.completionFlag.dataset.reached = reached ? "true" : "false";
    }
  }

  // ═══════════ Scenario presets ═══════════
  const presets = {
    "nominal-fwd": {
      label: "默认前向",
      apply: () => {
        setSlider(inputs.tra, 0);
        setSlider(inputs.ra, 100);
        setSlider(inputs.n1k, 35);
        setSlider(inputs.vdt, 0);
        setChecked(inputs.engineRunning, true);
        setChecked(inputs.aircraftOnGround, false);
        setChecked(inputs.reverserInhibited, false);
        setChecked(inputs.eecEnable, true);
        setSelect(inputs.feedbackMode, "auto_scrubber");
      },
    },
    "landing-deploy": {
      label: "着陆展开全链路",
      apply: () => {
        presets["nominal-fwd"].apply();
        setSlider(inputs.tra, -26);
        setSlider(inputs.ra, 2);
        setSlider(inputs.n1k, 70);
        setSlider(inputs.vdt, 95);
        setChecked(inputs.aircraftOnGround, true);
        setSelect(inputs.feedbackMode, "manual_feedback_override");
      },
    },
    "max-reverse": {
      label: "最大反推",
      apply: () => {
        presets["landing-deploy"].apply();
        setSlider(inputs.tra, -32);
        setSlider(inputs.n1k, 80);
        setSlider(inputs.vdt, 100);
      },
    },
    "stow-return": {
      label: "收起回杆",
      apply: () => {
        presets["nominal-fwd"].apply();
        setSlider(inputs.tra, 0);
        setSlider(inputs.ra, 2);
        setSlider(inputs.n1k, 25);
        setSlider(inputs.vdt, 30);
        setChecked(inputs.aircraftOnGround, true);
      },
    },
    "inhibit-block": {
      label: "抑制位阻塞",
      apply: () => {
        presets["landing-deploy"].apply();
        setChecked(inputs.reverserInhibited, true);
      },
    },
  };

  function setSlider(el, value) { if (el) el.value = String(value); }
  function setChecked(el, value) { if (el) el.checked = !!value; }
  function setSelect(el, value) { if (el) el.value = value; }

  function applyPreset(key) {
    const preset = presets[key];
    if (!preset) return;
    preset.apply();
    if (readouts.presetStatus) {
      readouts.presetStatus.textContent = "当前场景：" + preset.label;
    }
    document.querySelectorAll(".fan-preset-btn").forEach((btn) => {
      btn.setAttribute("aria-pressed", btn.dataset.preset === key ? "true" : "false");
    });
    fetchEvaluation();
  }

  // ═══════════ Wire listeners ═══════════
  function installListeners() {
    Object.values(inputs).forEach((el) => {
      if (!el) return;
      const evt = (el.type === "checkbox" || el.tagName === "SELECT") ? "change" : "input";
      el.addEventListener(evt, scheduleFetch);
    });
    document.querySelectorAll(".fan-preset-btn").forEach((btn) => {
      btn.addEventListener("click", () => applyPreset(btn.dataset.preset));
    });
  }

  function boot() {
    installListeners();
    fetchEvaluation();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();

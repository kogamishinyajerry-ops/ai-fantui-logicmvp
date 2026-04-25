/* FANTUI 反推逻辑演示舱 — demo.js
 *
 * Architecture: stateless signal-level evaluation via /api/lever-snapshot.
 * User moves TRA slider / toggles → debounced POST → render chain SVG + HUD
 * + output cards + status banner + tra_lock gate + fault injection.
 *
 * Phase UI-D (2026-04-22): replaced legacy ~2100-line demo.js.
 * Phase UI-H (2026-04-22): wire state coloring + gate icons + TRA lock + fault panel.
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
  };

  const readouts = {
    traValue:        $("fan-tra-value"),
    traZone:         $("fan-tra-zone"),
    raValue:         $("fan-ra-value"),
    n1kValue:        $("fan-n1k-value"),
    vdtValue:        $("fan-vdt-value"),
    statusBadge:     $("fan-status-badge"),
    statusSummary:   $("fan-status-summary"),
    completionFlag:  $("fan-completion-flag"),
    hudSw1:          $("fan-hud-sw1"),
    hudSw2:          $("fan-hud-sw2"),
    hudTls:          $("fan-hud-tls"),
    hudVdt90:        $("fan-hud-vdt90"),
    hudLogic:        $("fan-hud-logic"),
    hudThrLock:      $("fan-hud-thr-lock"),
    outTls115:       $("fan-out-tls115"),
    outTls115V:      $("fan-out-tls115-value"),
    outEtrac:        $("fan-out-etrac"),
    outEtracV:       $("fan-out-etrac-value"),
    outEec:          $("fan-out-eec"),
    outEecV:         $("fan-out-eec-value"),
    outThr:          $("fan-out-thr"),
    outThrV:         $("fan-out-thr-value"),
    presetStatus:    $("fan-preset-status"),
    traLockBadge:    $("fan-tra-lock-badge"),
    traLockRange:    $("fan-tra-lock-range"),
    traLockMsg:      $("fan-tra-lock-msg"),
    faultCount:      $("fan-fault-count"),
    faultActiveList: $("fan-fault-active-list"),
    vdtHint:         $("fan-vdt-hint"),
  };

  const chainSvg = document.getElementById("fan-chain-svg");

  // TRA deep-range lock state: -14° lock, -32° full range
  const TRA_LOCK_DEG = -14.0;
  let traLockActive = true;  // conservative default until first response

  function numValue(el, fallback) {
    if (!el) return fallback;
    const v = parseFloat(el.value);
    return Number.isFinite(v) ? v : fallback;
  }
  function checked(el) { return !!(el && el.checked); }

  // ═══════════ Fault injection ═══════════

  function buildFaultInjections() {
    const result = [];
    document.querySelectorAll(".fan-fault-check:checked").forEach((cb) => {
      const nodeId = cb.getAttribute("data-node");
      const faultType = cb.getAttribute("data-fault");
      if (nodeId && faultType) result.push({ node_id: nodeId, fault_type: faultType });
    });
    return result;
  }

  function renderFaultPanel() {
    const active = buildFaultInjections();
    if (readouts.faultCount) {
      readouts.faultCount.textContent = active.length > 0 ? `${active.length} 故障激活` : "0 故障";
      readouts.faultCount.dataset.active = active.length > 0 ? "true" : "false";
    }
    if (readouts.faultActiveList) {
      readouts.faultActiveList.textContent = active.length > 0
        ? active.map((f) => `${f.node_id}:${f.fault_type}`).join("  ·  ")
        : "";
    }
    // Highlight active rows
    document.querySelectorAll(".fan-fault-row").forEach((row) => {
      const cb = row.querySelector(".fan-fault-check");
      row.dataset.active = cb && cb.checked ? "true" : "false";
    });
  }

  // ═══════════ Request builder ═══════════

  function buildRequest() {
    // E11-14 (2026-04-25): /api/lever-snapshot now requires actor + ticket_id +
    // manual_override_signoff when feedback_mode = manual_feedback_override.
    // Demo flow ships canned sign-off matching the demo Approval Center exit
    // state (Kogami signed WB-DEMO at deploy). Real UI will fill these from
    // the sign-off ticket post-E11-08.
    return {
      tra_deg:                  numValue(inputs.tra, 0),
      radio_altitude_ft:        numValue(inputs.ra, 0),
      n1k:                      numValue(inputs.n1k, 0.35) / 100,
      engine_running:           checked(inputs.engineRunning),
      aircraft_on_ground:       checked(inputs.aircraftOnGround),
      reverser_inhibited:       checked(inputs.reverserInhibited),
      eec_enable:               checked(inputs.eecEnable),
      feedback_mode:            "manual_feedback_override",
      actor:                    "Kogami",
      ticket_id:                "WB-DEMO",
      manual_override_signoff:  {
        signed_by: "Kogami",
        signed_at: "2026-04-25T00:00:00Z",
        ticket_id: "WB-DEMO",
      },
      deploy_position_percent:  numValue(inputs.vdt, 0),
      fault_injections:         buildFaultInjections(),
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
    if (inflight) { nextRequest = true; return; }
    inflight = true;
    const payload = buildRequest();
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) { console.warn("[demo] snapshot eval failed:", response.status); return; }
      const data = await response.json();
      renderAll(data, payload);
    } catch (err) {
      console.warn("[demo] fetch error:", err);
    } finally {
      inflight = false;
      if (nextRequest) { nextRequest = false; fetchEvaluation(); }
    }
  }

  function scheduleFetch() {
    if (pending) clearTimeout(pending);
    pending = setTimeout(() => { pending = null; fetchEvaluation(); }, DEBOUNCE_MS);
  }

  // ═══════════ Rendering ═══════════
  function renderAll(data, request) {
    const nodes = Array.isArray(data.nodes) ? data.nodes : [];
    const nodeById = new Map(nodes.map((n) => [n.id, n]));

    renderLeverHud(request, data);
    renderTraLock(data);
    renderChain(nodeById);
    renderOutputs(nodeById);
    renderHud(nodeById);
    renderStatus(data, nodeById);
    renderFaultPanel();
  }

  function renderLeverHud(req, data) {
    if (readouts.traValue) readouts.traValue.textContent = req.tra_deg.toFixed(1) + "°";
    if (readouts.traZone) {
      const [zone, label] = zoneFromTra(req.tra_deg);
      readouts.traZone.dataset.zone = zone;
      readouts.traZone.textContent = label;
    }
    if (readouts.raValue)  readouts.raValue.textContent  = req.radio_altitude_ft.toFixed(0) + " ft";
    if (readouts.n1kValue) readouts.n1kValue.textContent = (req.n1k * 100).toFixed(0) + "%";
    if (readouts.vdtValue) {
      // Prefer the backend's echoed VDT from hud.deploy_position_percent; fall
      // back to the request slider if the response is missing it for any reason.
      const hudVdt = data && data.hud && typeof data.hud.deploy_position_percent === "number"
        ? data.hud.deploy_position_percent
        : req.deploy_position_percent;
      readouts.vdtValue.textContent = hudVdt.toFixed(0) + "%";
    }
  }

  // ═══════════ TRA=-14° lock rendering ═══════════

  function renderTraLock(data) {
    const lock = data.tra_lock;
    if (!lock || typeof lock !== "object") return;

    const locked    = Boolean(lock.locked);
    const unlockMsg = lock.message || (
      locked
        ? "TRA 自由区 -14°~0°；满足 VDT≥90% (L4) 后才开放 -32°~-14° 深拉区。"
        : "L4 已满足：TRA 深拉区 -32°~-14° 已开放，可继续向左推进。"
    );
    const effectiveTra = Number(lock.effective_tra_deg ?? numValue(inputs.tra, 0));

    traLockActive = locked;

    // Clamp slider value to effective (server may have clamped request)
    if (inputs.tra && Math.abs(parseFloat(inputs.tra.value) - effectiveTra) > 0.1) {
      inputs.tra.value = String(effectiveTra);
      if (readouts.traValue) readouts.traValue.textContent = effectiveTra.toFixed(1) + "°";
    }

    if (readouts.traLockBadge) {
      readouts.traLockBadge.textContent = locked ? "深拉区关闭" : "深拉区已开放";
      readouts.traLockBadge.dataset.locked = locked ? "true" : "false";
    }
    if (readouts.traLockRange) {
      const visualMin = Number(lock.visual_reverse_min_deg ?? -32);
      const gateMin   = Number(lock.allowed_reverse_min_deg ?? TRA_LOCK_DEG);
      readouts.traLockRange.textContent = locked
        ? `条件深拉区 ${visualMin.toFixed(0)}°~${gateMin.toFixed(0)}°（关闭）`
        : `条件深拉区 ${visualMin.toFixed(0)}°~${gateMin.toFixed(0)}°（已开放）`;
      readouts.traLockRange.dataset.locked = locked ? "true" : "false";
    }
    if (readouts.traLockMsg) readouts.traLockMsg.textContent = unlockMsg;
  }

  // Guard slider drag past -14° while locked
  function guardTraSlider() {
    if (!inputs.tra) return;
    const v = parseFloat(inputs.tra.value);
    if (traLockActive && v < TRA_LOCK_DEG) {
      inputs.tra.value = String(TRA_LOCK_DEG);
    }
  }

  // ═══════════ Chain SVG: nodes + wires + junctions ═══════════

  function nodeActive(nodeById, id) {
    if (!id) return false;
    const n = nodeById.get(id);
    return n ? n.state === "active" : false;
  }

  function renderChain(nodeById) {
    if (!chainSvg) return;

    // 1. Node / logic block state
    chainSvg.querySelectorAll(".chain-node, .chain-logic").forEach((group) => {
      const nodeId = group.getAttribute("data-node");
      const node = nodeById.get(nodeId);
      group.dataset.state = node ? (node.state || "idle") : "idle";
    });

    // 2. Wire state coloring
    chainSvg.querySelectorAll(".chain-wire").forEach((wire) => {
      const src = wire.getAttribute("data-src");
      const dst = wire.getAttribute("data-dst");
      const isFault = wire.getAttribute("data-fault") === "true";
      const srcActive = nodeActive(nodeById, src);
      const dstActive = nodeActive(nodeById, dst);

      let state = "idle";
      if (isFault && srcActive)          state = "fault";
      else if (srcActive && dstActive)   state = "active";
      else if (srcActive)                state = "active";  // src lit → wire lit even if dst not yet

      wire.dataset.state = state;
      if (state === "active")      wire.setAttribute("marker-end", "url(#fan-arr-active)");
      else if (state === "fault")  wire.setAttribute("marker-end", "url(#fan-arr-fault)");
      else                         wire.setAttribute("marker-end", "url(#fan-arr-idle)");
    });

    // 3. Junction dots inherit src state; fault-bus junctions turn red when source is asserted
    chainSvg.querySelectorAll(".chain-junction").forEach((dot) => {
      const src = dot.getAttribute("data-src");
      const isFault = dot.getAttribute("data-fault") === "true";
      const srcActive = nodeActive(nodeById, src);
      if (isFault && srcActive) dot.dataset.state = "fault";
      else dot.dataset.state = srcActive ? "active" : "idle";
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
    const thr    = nodeById.get("thr_lock");
    const logic4 = nodeById.get("logic4");
    const logic3 = nodeById.get("logic3");
    const inhibited = checked(inputs.reverserInhibited);
    const faults    = buildFaultInjections();

    let state = "idle";
    let summary = "等待拉杆快照 …";
    let reached = false;

    if (faults.length > 0 && (thr ? thr.state !== "active" : true)) {
      const names = faults.map((f) => `${f.node_id}:${f.fault_type}`).join(" + ");
      if (thr && thr.state === "blocked") {
        state = "fault";
        summary = `故障注入激活 [${names}]：THR_LOCK 封锁。`;
      } else {
        state = "fault";
        summary = `故障注入激活 [${names}]：链路降级。`;
      }
    } else if (inhibited) {
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
      summary = "L3 激活：EEC deploy / PLS / PDU 通电。等待 VDT≥90% 解锁深拉区。";
    } else if (nodeById.get("logic2") && nodeById.get("logic2").state === "active") {
      state = "ready";
      summary = "L2 激活：ETRAC 540VDC 已供电，等待 L3 条件。";
    } else if (nodeById.get("logic1") && nodeById.get("logic1").state === "active") {
      state = "ready";
      summary = "L1 激活：TLS 115VAC 已供电。等待 L2 条件（SW2 + engine_running + TLS 解锁）。";
    } else {
      state = "idle";
      summary = traLockActive
        ? "TRA 在自由区（-14°~0°）；拉到 -14° 后等待 VDT≥90% 才能进入深拉区。"
        : "等待输入：TRA / RA / aircraft_on_ground 未满足 L1 前置条件。";
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
        clearAllFaults();
      },
    },
    "landing-deploy": {
      label: "着陆展开全链路",
      apply: () => {
        presets["nominal-fwd"].apply();
        setSlider(inputs.tra, -26);
        setSlider(inputs.ra, 2);
        setSlider(inputs.n1k, 70);
        // VDT=0 at preset load: L1 (!DEP) + L2 + L3 all active, L4 waiting
        // for VDT90. Drag VDT up to watch L1 correctly release (!DEP flips
        // false after deployment) and L4 fire — the true deployment cycle.
        setSlider(inputs.vdt, 0);
        setChecked(inputs.aircraftOnGround, true);
      },
    },
    "max-reverse": {
      label: "最大反推（展开到位）",
      apply: () => {
        presets["landing-deploy"].apply();
        // TRA=-32 is the mechanical stop and is inclusive in the L4 range
        // [-32, 0), so L4 correctly engages at the slider's leftmost value.
        setSlider(inputs.tra, -32);
        setSlider(inputs.n1k, 80);
        // VDT=100 shows the POST-deploy state: L4 active / THR_LOCK released.
        // L1 correctly drops to blocked because `!DEP` flipped — L1 has
        // already done its job and no longer asserts TLS unlock.
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

  function clearAllFaults() {
    document.querySelectorAll(".fan-fault-check").forEach((cb) => { cb.checked = false; });
    renderFaultPanel();
  }

  function applyPreset(key) {
    const preset = presets[key];
    if (!preset) return;
    preset.apply();
    if (readouts.presetStatus) readouts.presetStatus.textContent = "当前场景：" + preset.label;
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

    // TRA slider: guard deep-range while locked
    if (inputs.tra) {
      inputs.tra.addEventListener("input", guardTraSlider);
    }

    document.querySelectorAll(".fan-preset-btn").forEach((btn) => {
      btn.addEventListener("click", () => applyPreset(btn.dataset.preset));
    });

    // Fault injection checkboxes
    document.querySelectorAll(".fan-fault-check").forEach((cb) => {
      cb.addEventListener("change", () => { renderFaultPanel(); scheduleFetch(); });
    });

    const clearBtn = $("fan-fault-clear");
    if (clearBtn) clearBtn.addEventListener("click", () => { clearAllFaults(); scheduleFetch(); });
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

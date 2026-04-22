/* C919 E-TRAS Logic Workstation — JS runtime.
 *
 * Architecture: stateless signal-level evaluation.
 * - User moves inputs (TRA slider / N1K / lock toggles / timing inputs).
 * - Debounced → POST /api/system-snapshot with system_id=c919-etras + snapshot.
 * - Backend adapter returns truth_evaluation (active logic ids + asserted values).
 * - Render: HUD values, SVG node states, output cards, overall status banner.
 *
 * Not stateful: no tick loop, no state machine replay. For dynamic state
 * machine visualization, use the :9191 simulation panel.
 */
(function () {
  "use strict";

  const API_URL = "/api/system-snapshot";
  const SYSTEM_ID = "c919-etras";
  const DEBOUNCE_MS = 120;

  // ═══════════ Input DOM references ═══════════
  const $ = (id) => document.getElementById(id);

  const inputs = {
    tra:                 $("etras-tra-lever"),
    n1k:                 $("etras-n1k"),
    engineRunning:       $("etras-engine-running"),
    trInhibited:         $("etras-tr-inhibited"),
    overTempFault:       $("etras-over-temp-fault"),
    trcuPowerOn:         $("etras-trcu-power-on"),
    vdtValid:            $("etras-vdt-valid"),
    lgcu1Value:          $("etras-lgcu1-value"),
    lgcu1Valid:          $("etras-lgcu1-valid"),
    lgcu2Value:          $("etras-lgcu2-value"),
    lgcu2Valid:          $("etras-lgcu2-valid"),
    tlsAUnlocked:        $("etras-tls-a-unlocked"),
    tlsBUnlocked:        $("etras-tls-b-unlocked"),
    plsALocked:          $("etras-pls-a-locked"),
    plsBLocked:          $("etras-pls-b-locked"),
    leftPylonAUnlocked:  $("etras-left-pylon-a-unlocked"),
    leftPylonBUnlocked:  $("etras-left-pylon-b-unlocked"),
    rightPylonAUnlocked: $("etras-right-pylon-a-unlocked"),
    rightPylonBUnlocked: $("etras-right-pylon-b-unlocked"),
    trPosition:          $("etras-tr-position"),
    comm2Timer:          $("etras-comm2-timer"),
    unlockConfirm:       $("etras-unlock-confirm"),
    deployedConfirm:     $("etras-deployed-confirm"),
    stowedConfirm:       $("etras-stowed-confirm"),
    prevCmd3:            $("etras-prev-cmd3"),
    trWow:               $("etras-tr-wow"),
  };

  // ═══════════ Output DOM references ═══════════
  const readouts = {
    traValue:         $("etras-tra-value"),
    traZone:          $("etras-tra-zone"),
    n1kValue:         $("etras-n1k-value"),
    trPositionValue:  $("etras-tr-position-value"),
    statusBadge:      $("etras-status-badge"),
    statusSummary:    $("etras-status-summary"),
    completionFlag:   $("etras-completion-flag"),
    hudMlgWow:        $("hud-mlg-wow"),
    hudTrWow:         $("hud-tr-wow"),
    hudSwitches:      $("hud-switches"),
    hudLockState:     $("hud-lock-state"),
    hudCmd2Timer:     $("hud-cmd2-timer"),
    hudCmd3Latch:     $("hud-cmd3-latch"),
    hudCmd3Enable:    $("hud-cmd3-enable"),
    hudTrPosition:    $("hud-tr-position"),
    hudN1k:           $("hud-n1k"),
    hudFaults:        $("hud-faults"),
    outSinglePhase:   $("output-single-phase"),
    outThreePhase:    $("output-three-phase"),
    outFadecDeploy:   $("output-fadec-deploy"),
    outFadecStow:     $("output-fadec-stow"),
    outSinglePhaseV:  $("output-single-phase-value"),
    outThreePhaseV:   $("output-three-phase-value"),
    outFadecDeployV:  $("output-fadec-deploy-value"),
    outFadecStowV:    $("output-fadec-stow-value"),
    presetStatus:     $("etras-preset-status"),
  };

  const chainSvg = document.getElementById("etras-logic-chain");

  // ═══════════ Helpers ═══════════
  function checked(el) { return !!(el && el.checked); }
  function numValue(el, fallback) {
    if (!el) return fallback;
    const v = parseFloat(el.value);
    return Number.isFinite(v) ? v : fallback;
  }

  function buildSnapshot() {
    return {
      tra_deg:                    numValue(inputs.tra, 0),
      n1k_percent:                numValue(inputs.n1k, 35),
      engine_running:             checked(inputs.engineRunning),
      tr_inhibited:               checked(inputs.trInhibited),
      lgcu1_mlg_wow_value:        checked(inputs.lgcu1Value),
      lgcu1_mlg_wow_valid:        checked(inputs.lgcu1Valid),
      lgcu2_mlg_wow_value:        checked(inputs.lgcu2Value),
      lgcu2_mlg_wow_valid:        checked(inputs.lgcu2Valid),
      tr_wow:                     checked(inputs.trWow),
      tls_ls_a_valid:             true,
      tls_ls_a_unlocked:          checked(inputs.tlsAUnlocked),
      tls_ls_b_valid:             true,
      tls_ls_b_unlocked:          checked(inputs.tlsBUnlocked),
      pls_ls_a_locked:            checked(inputs.plsALocked),
      pls_ls_b_locked:            checked(inputs.plsBLocked),
      left_pylon_ls_a_valid:      true,
      left_pylon_ls_a_unlocked:   checked(inputs.leftPylonAUnlocked),
      left_pylon_ls_b_valid:      true,
      left_pylon_ls_b_unlocked:   checked(inputs.leftPylonBUnlocked),
      right_pylon_ls_a_valid:     true,
      right_pylon_ls_a_unlocked:  checked(inputs.rightPylonAUnlocked),
      right_pylon_ls_b_valid:     true,
      right_pylon_ls_b_unlocked:  checked(inputs.rightPylonBUnlocked),
      apwtla:                     computeApwtla(numValue(inputs.tra, 0)),
      atltla:                     computeAtltla(numValue(inputs.tra, 0)),
      vdt_sensor_valid:           checked(inputs.vdtValid),
      e_tras_over_temp_fault:     checked(inputs.overTempFault),
      trcu_power_on:              checked(inputs.trcuPowerOn),
      tr_position_percent:        numValue(inputs.trPosition, 0),
      prev_eicu_cmd3:             checked(inputs.prevCmd3),
      comm2_timer_s:              numValue(inputs.comm2Timer, 0),
      lock_unlock_confirm_s:      numValue(inputs.unlockConfirm, 0),
      tr_position_deployed_confirm_s: numValue(inputs.deployedConfirm, 0),
      tr_stowed_locked_confirm_s: numValue(inputs.stowedConfirm, 2),
    };
  }

  // SW1: ATLTLA closes when TRA ∈ [-6.2, -1.4]
  function computeAtltla(tra) { return tra <= -1.4 && tra >= -6.2; }
  // SW2: APWTLA closes when TRA ∈ [-9.8, -5.0]
  function computeApwtla(tra) { return tra <= -5.0 && tra >= -9.8; }

  function zoneFromTra(tra) {
    if (tra <= -25)   return ["max-rev",  "MAX REV"];
    if (tra <= -11.74)return ["rev-idle", "REV IDLE"];
    if (tra <= -6.2)  return ["sw2",      "SW1+SW2"];
    if (tra <= -5.0)  return ["sw2",      "SW2 ONLY"];
    if (tra <= -1.4)  return ["sw1",      "SW1 ONLY"];
    if (tra < 0)      return ["fwd-idle", "FWD IDLE"];
    return ["fwd", "FWD"];
  }

  function formatBool(value) {
    if (value === true)  return "TRUE";
    if (value === false) return "false";
    return "—";
  }
  function formatPct(value, digits = 0) {
    if (typeof value !== "number") return "—";
    return value.toFixed(digits) + "%";
  }

  // ═══════════ Fetch + render pipeline ═══════════
  let pending = null;
  let inflight = false;
  let nextRequest = null;

  async function fetchEvaluation() {
    if (inflight) {
      nextRequest = true;
      return;
    }
    inflight = true;
    const snapshot = buildSnapshot();
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ system_id: SYSTEM_ID, snapshot }),
      });
      if (!response.ok) {
        console.warn("[c919-workstation] snapshot eval failed:", response.status);
        return;
      }
      const payload = await response.json();
      renderAll(payload, snapshot);
    } catch (err) {
      console.warn("[c919-workstation] fetch error:", err);
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
  function renderAll(payload, snapshot) {
    const evaluation = payload.truth_evaluation || {};
    const asserted   = evaluation.asserted_component_values || {};
    const activeIds  = new Set(evaluation.active_logic_node_ids || []);
    const summary    = evaluation.summary || "";
    const completion = evaluation.completion_reached === true;

    renderLeverHud(snapshot);
    renderHud(asserted, snapshot);
    renderOutputs(asserted);
    renderChainSvg(activeIds, asserted);
    renderStatusBanner(summary, completion, asserted);
  }

  function renderLeverHud(snapshot) {
    if (readouts.traValue) readouts.traValue.textContent = snapshot.tra_deg.toFixed(1) + "°";
    if (readouts.n1kValue) readouts.n1kValue.textContent = snapshot.n1k_percent.toFixed(0) + "%";
    if (readouts.trPositionValue) readouts.trPositionValue.textContent = snapshot.tr_position_percent.toFixed(0) + "%";
    if (readouts.traZone) {
      const [zone, label] = zoneFromTra(snapshot.tra_deg);
      readouts.traZone.dataset.zone = zone;
      readouts.traZone.textContent = label;
    }
  }

  function renderHud(asserted, snapshot) {
    setHud(readouts.hudMlgWow, asserted.mlg_wow);
    setHud(readouts.hudTrWow,  asserted.tr_wow);
    if (readouts.hudSwitches) {
      const sw1 = asserted.atltla ? "SW1:ON" : "SW1:off";
      const sw2 = asserted.apwtla ? "SW2:ON" : "SW2:off";
      readouts.hudSwitches.textContent = `${sw1} · ${sw2}`;
      readouts.hudSwitches.dataset.flag = (asserted.atltla || asserted.apwtla) ? "true" : "false";
    }
    if (readouts.hudLockState) {
      readouts.hudLockState.textContent = asserted.lock_state || "—";
      readouts.hudLockState.dataset.flag = (asserted.lock_state === "UNLOCKED_CONFIRMED") ? "true" : "false";
    }
    if (readouts.hudCmd2Timer) {
      readouts.hudCmd2Timer.textContent = snapshot.comm2_timer_s.toFixed(1) + " / 30.0";
    }
    if (readouts.hudCmd3Latch) {
      readouts.hudCmd3Latch.textContent = snapshot.prev_eicu_cmd3 ? "latched" : "reset";
      readouts.hudCmd3Latch.dataset.flag = snapshot.prev_eicu_cmd3 ? "true" : "false";
    }
    setHud(readouts.hudCmd3Enable, asserted.tr_command3_enable);
    if (readouts.hudTrPosition) {
      const pct = typeof asserted.tr_position_percent === "number"
        ? asserted.tr_position_percent : snapshot.tr_position_percent;
      readouts.hudTrPosition.textContent = `${pct.toFixed(0)}% / 80%`;
      readouts.hudTrPosition.dataset.flag = pct >= 80 ? "true" : "false";
    }
    if (readouts.hudN1k) {
      const n1k = typeof asserted.n1k_percent === "number" ? asserted.n1k_percent : snapshot.n1k_percent;
      readouts.hudN1k.textContent = `${n1k.toFixed(0)}% / 84%`;
      readouts.hudN1k.dataset.flag = n1k <= 84 ? "true" : "false";
    }
    if (readouts.hudFaults) {
      const parts = [];
      if (asserted.e_tras_over_temp_fault) parts.push("过温");
      if (asserted.tr_inhibited) parts.push("抑制");
      readouts.hudFaults.textContent = parts.length ? parts.join(" / ") : "正常";
      readouts.hudFaults.dataset.flag = parts.length ? "fault" : "true";
    }
  }

  function setHud(el, value) {
    if (!el) return;
    el.textContent = formatBool(value);
    el.dataset.flag = value === true ? "true" : "false";
  }

  function renderOutputs(asserted) {
    setOutputCard(readouts.outSinglePhase,  readouts.outSinglePhaseV, asserted.eicu_cmd2,             "active");
    setOutputCard(readouts.outThreePhase,   readouts.outThreePhaseV,  asserted.eicu_cmd3,             "active");
    setOutputCard(readouts.outFadecDeploy,  readouts.outFadecDeployV, asserted.fadec_deploy_command,  "active");
    setOutputCard(readouts.outFadecStow,    readouts.outFadecStowV,   asserted.fadec_stow_command,    "stow");
  }

  function setOutputCard(card, valueEl, asserted, activeState) {
    if (!card || !valueEl) return;
    const on = asserted === true;
    card.dataset.state = on ? activeState : "idle";
    valueEl.textContent = on ? "ON" : "OFF";
  }

  function renderChainSvg(activeIds, asserted) {
    if (!chainSvg) return;
    // Logic gates
    chainSvg.querySelectorAll(".chain-logic").forEach((group) => {
      const nodeId = group.getAttribute("data-node");
      group.dataset.state = activeIds.has(nodeId) ? "active" : "idle";
    });
    // Input / output chain nodes keyed by component id
    chainSvg.querySelectorAll(".chain-node").forEach((group) => {
      const nodeId = group.getAttribute("data-node");
      const value = asserted[nodeId];
      const active = isTruthyComponent(nodeId, value);
      group.dataset.state = active ? "active" : "idle";
    });
  }

  function isTruthyComponent(id, value) {
    if (value === true) return true;
    if (id === "lock_state") return value === "UNLOCKED_CONFIRMED";
    if (id === "tra_deg") return typeof value === "number" && value < -1.4;
    if (id === "tr_position_percent") return typeof value === "number" && value > 0;
    if (id === "n1k_percent") return typeof value === "number" && value > 0;
    return false;
  }

  function renderStatusBanner(summary, completion, asserted) {
    if (readouts.statusSummary && summary) readouts.statusSummary.textContent = summary;
    if (readouts.completionFlag) {
      readouts.completionFlag.textContent = completion ? "已达成" : "未达成";
      readouts.completionFlag.dataset.reached = completion ? "true" : "false";
    }
    if (readouts.statusBadge) {
      const state = inferBadgeState(asserted, completion);
      readouts.statusBadge.dataset.state = state;
      readouts.statusBadge.textContent = badgeText(state);
    }
  }

  function inferBadgeState(asserted, completion) {
    if (asserted.e_tras_over_temp_fault || asserted.tr_inhibited) return "fault";
    if (asserted.fadec_deploy_command && completion) return "deployed";
    if (asserted.fadec_deploy_command) return "deploying";
    if (asserted.fadec_stow_command) return "stowing";
    if (asserted.eicu_cmd3 || asserted.eicu_cmd2) return "ready";
    return "idle";
  }

  function badgeText(state) {
    return ({
      idle:      "IDLE",
      ready:     "READY",
      deploying: "DEPLOYING",
      deployed:  "DEPLOYED",
      stowing:   "STOWING",
      fault:     "FAULT",
    })[state] || "IDLE";
  }

  // ═══════════ Scenario presets ═══════════
  const presets = {
    "nominal-stowed": {
      label: "默认（空中收起上锁）",
      apply: () => {
        setSlider(inputs.tra, 0);
        setSlider(inputs.n1k, 35);
        setSlider(inputs.trPosition, 0);
        setChecked(inputs.engineRunning, true);
        setChecked(inputs.trInhibited, false);
        setChecked(inputs.overTempFault, false);
        setChecked(inputs.trcuPowerOn, true);
        setChecked(inputs.vdtValid, true);
        setChecked(inputs.lgcu1Value, true);
        setChecked(inputs.lgcu1Valid, true);
        setChecked(inputs.lgcu2Value, true);
        setChecked(inputs.lgcu2Valid, true);
        setChecked(inputs.trWow, true);
        setChecked(inputs.tlsAUnlocked, false);
        setChecked(inputs.tlsBUnlocked, false);
        setChecked(inputs.plsALocked, true);
        setChecked(inputs.plsBLocked, true);
        setChecked(inputs.leftPylonAUnlocked, false);
        setChecked(inputs.leftPylonBUnlocked, false);
        setChecked(inputs.rightPylonAUnlocked, false);
        setChecked(inputs.rightPylonBUnlocked, false);
        setChecked(inputs.prevCmd3, false);
        setNumber(inputs.comm2Timer, 0);
        setNumber(inputs.unlockConfirm, 0);
        setNumber(inputs.deployedConfirm, 0);
        setNumber(inputs.stowedConfirm, 2);
      },
    },
    "landing-deploy": {
      label: "着陆展开全链路",
      apply: () => {
        presets["nominal-stowed"].apply();
        setSlider(inputs.tra, -25.0);
        setSlider(inputs.n1k, 60);
        setSlider(inputs.trPosition, 85);
        // Unlocks propagated
        setChecked(inputs.tlsAUnlocked, true);
        setChecked(inputs.tlsBUnlocked, true);
        setChecked(inputs.plsALocked, false);
        setChecked(inputs.plsBLocked, false);
        setChecked(inputs.leftPylonAUnlocked, true);
        setChecked(inputs.leftPylonBUnlocked, true);
        setChecked(inputs.rightPylonAUnlocked, true);
        setChecked(inputs.rightPylonBUnlocked, true);
        // Timing passed
        setNumber(inputs.comm2Timer, 1.0);
        setNumber(inputs.unlockConfirm, 0.5);
        setNumber(inputs.deployedConfirm, 0.5);
        setNumber(inputs.stowedConfirm, 0);
        setChecked(inputs.prevCmd3, true);
      },
    },
    "max-reverse": {
      label: "最大反推（MAX REV）",
      apply: () => {
        presets["landing-deploy"].apply();
        setSlider(inputs.tra, -32.0);
        setSlider(inputs.n1k, 90);
        setSlider(inputs.trPosition, 100);
      },
    },
    "stow-return": {
      label: "收起回杆",
      apply: () => {
        presets["nominal-stowed"].apply();
        setSlider(inputs.tra, 0);
        setSlider(inputs.n1k, 45);
        setSlider(inputs.trPosition, 30);  // mid-stow
        setChecked(inputs.prevCmd3, true);
        setChecked(inputs.tlsAUnlocked, true);
        setChecked(inputs.tlsBUnlocked, true);
        setChecked(inputs.plsALocked, false);
        setChecked(inputs.plsBLocked, false);
        setChecked(inputs.leftPylonAUnlocked, true);
        setChecked(inputs.leftPylonBUnlocked, true);
        setChecked(inputs.rightPylonAUnlocked, true);
        setChecked(inputs.rightPylonBUnlocked, true);
        setNumber(inputs.stowedConfirm, 0);
      },
    },
    "over-temp-abort": {
      label: "过温中断",
      apply: () => {
        presets["landing-deploy"].apply();
        setChecked(inputs.overTempFault, true);
      },
    },
    "lock-fault": {
      label: "锁传感器故障（解锁不一致）",
      apply: () => {
        presets["nominal-stowed"].apply();
        setSlider(inputs.tra, -15.0);
        setSlider(inputs.n1k, 60);
        // Partial unlock — TLS yes but pylons still locked
        setChecked(inputs.tlsAUnlocked, true);
        setChecked(inputs.tlsBUnlocked, true);
        setChecked(inputs.plsALocked, false);
        setChecked(inputs.plsBLocked, false);
        setChecked(inputs.leftPylonAUnlocked, true);
        setChecked(inputs.leftPylonBUnlocked, true);
        setChecked(inputs.rightPylonAUnlocked, false);  // fault: right pylon did not unlock
        setChecked(inputs.rightPylonBUnlocked, false);
        setNumber(inputs.comm2Timer, 1.0);
      },
    },
  };

  function setSlider(el, value) { if (el) el.value = String(value); }
  function setNumber(el, value) { if (el) el.value = String(value); }
  function setChecked(el, value) { if (el) el.checked = !!value; }

  function applyPreset(key) {
    const preset = presets[key];
    if (!preset) return;
    preset.apply();
    if (readouts.presetStatus) {
      readouts.presetStatus.textContent = "当前场景：" + preset.label;
    }
    document.querySelectorAll(".preset-btn").forEach((btn) => {
      btn.setAttribute("aria-pressed", btn.dataset.preset === key ? "true" : "false");
    });
    // Immediate fetch after preset (no debounce — single batched snapshot)
    fetchEvaluation();
  }

  // ═══════════ Wire input listeners ═══════════
  function installListeners() {
    Object.values(inputs).forEach((el) => {
      if (!el) return;
      const evt = el.type === "checkbox" ? "change" : "input";
      el.addEventListener(evt, scheduleFetch);
    });
    document.querySelectorAll(".preset-btn").forEach((btn) => {
      btn.addEventListener("click", () => applyPreset(btn.dataset.preset));
    });
  }

  // ═══════════ Bootstrap ═══════════
  function boot() {
    installListeners();
    fetchEvaluation();  // initial render
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();

# C919 E-TRAS Traceability Matrix · P34-04

Audit-grade mapping from the 甲方 requirement PDF (`uploads/20260417-C919反推控制逻辑需求文档.pdf`, 10 pages) to the executable truth adapter (`src/well_harness/adapters/c919_etras_adapter.py`) and the validation suite (`tests/test_c919_etras_adapter.py`).

Three sources of truth are cross-linked by every row below:

1. **PDF anchor** — `§` / `图` / `表` / `Step` tag pointing at the 10-page PDF.
2. **Adapter anchor** — file + line number in `src/well_harness/adapters/c919_etras_adapter.py` (LOC references are rechecked in each P34-05 closure).
3. **Test anchor** — class + function name in `tests/test_c919_etras_adapter.py`.

Hardware constants and thresholds are mirrored from `config/hardware/c919_etras_hardware_v1.yaml`; any PDF update must propagate to both the YAML and the adapter in the same commit.

---

## Table 1 · PDF signals → adapter snapshot fields → ComponentSpec id

| # | PDF anchor | Signal (PDF terminology) | Snapshot key (adapter) | ComponentSpec `id` | Adapter LOC | Test(s) |
|---|---|---|---|---|---|---|
| 1 | PDF 表2 + §1.1.1 ① | MLG_WOW (LGCU1/LGCU2 redundancy resolved) | `mlg_wow_lgcu1`, `mlg_wow_lgcu1_valid`, `mlg_wow_lgcu2`, `mlg_wow_lgcu2_valid` → `_select_mlg_wow` | `mlg_wow` | 278 | `MLGWOWRedundancySelectionTests` (246–269) |
| 2 | PDF §1.1.1 ② | TR inhibited (A/C-bus hardwire) | `tr_inhibited` | `tr_inhibited` | 291 | `test_cmd2_blocked_when_tr_inhibited` (291); `test_cmd3_resets_immediately_on_tr_inhibited` (327) |
| 3 | PDF §1.1.3 ⑥ / §Step2 | TRA (throttle resolver angle, deg) | `tra_deg` | `tra_deg` | 302 | `TRCommand3EnableGatingTests::test_enable_blocked_by_tra_at_or_above_fwd_idle` (361); `FADECDeployCommandGatingTests::test_deploy_blocked_by_tra_above_reverse_idle` (422) |
| 4 | PDF §Step2 (图3) | ATLTLA (aft-throttle lever idle — microswitch 1, closed when TRA ∈ [-1.4°, -6.2°]) | `atltla` | `atltla` | 315 | `EICUCMD2TruthTableTests::test_cmd2_asserts_with_atltla_or_apwtla_on_ground_not_inhibited` (280) |
| 5 | PDF §Step2 (图3) | APWTLA (aft-push thrust lever — microswitch 2, closed when TRA ∈ [-5°, -9.8°]) | `apwtla` | `apwtla` | 328 | `EICUCMD2TruthTableTests::test_cmd2_asserts_with_atltla_or_apwtla_on_ground_not_inhibited` (280) |
| 6 | PDF §1.1.1 ④ / §Step4 | TR_Deployed position (VDT sensor, 0–100%) | `tr_position_percent`, `tr_position_confirm_s` | `tr_position_percent` | 339 | `FADECDeployCommandGatingTests::test_deploy_blocked_by_tr_position_below_80pct` (395); `FaultInjectionTests::test_fault_vdt_sensor_bias_low` (627) |
| 7 | PDF §1.1.3 ③ | TLS + left pylon + right pylon lock status (deployed / stowed / unlocked) | `tls_left_unlocked`, `tls_right_unlocked`, `tls_left_valid`, `tls_right_valid`, `left_pylon_unlocked_a`, `left_pylon_unlocked_b`, `left_pylon_valid_a`, `left_pylon_valid_b`, `right_pylon_unlocked_a`, `right_pylon_unlocked_b`, `right_pylon_valid_a`, `right_pylon_valid_b`, `pls_left_locked`, `pls_right_locked`, `lock_unlock_confirm_s` → `_tls_unlocked_confirmed`, `_pylon_locks_unlocked_confirmed`, `_pls_both_locked` | `lock_state` | 352 | `LockFallbackTruthTableTests` (480–514) |
| 8 | PDF §1.1.2 ① | Engine running (at or above idle) | `engine_running` | `engine_running` | 369 | `FADECDeployCommandGatingTests::test_deploy_blocked_by_engine_not_running` (408); `FADECStowCommandGatingTests::test_stow_blocked_when_engine_not_running` (449) |
| 9 | PDF §1.1.3 ⑤ | N1k (normalized core speed, 0–100%) | `n1k_percent` | `n1k_percent` | 379 | `FADECDeployCommandGatingTests::test_deploy_blocked_by_n1k_at_or_above_deploy_limit` (411); `FADECStowCommandGatingTests::test_stow_blocked_when_n1k_above_stow_limit` (446) |
| 10 | PDF §1.1.3 ④ | TR_WOW (in-flight inhibit after 2.25 s TRUE / 120 ms FALSE) | `tr_wow`, `tr_wow_true_persist_s`, `tr_wow_false_persist_s` | `tr_wow` | 392 | `FADECDeployCommandGatingTests::test_deploy_blocked_by_tr_wow_false` (419) |
| 11 | PDF §1.1.1 图2 | TRCU power-on (115 VAC 3-phase) | `trcu_power_on` | `trcu_power_on` | 405 | Implicit via EICU CMD2 chain (`EICUCMD2TruthTableTests`) |
| 12 | PDF §1.1.2 图4 ④ | E-TRAS over-temperature fault word | `e_tras_over_temp_fault` | `e_tras_over_temp_fault` | 415 | `TRCommand3EnableGatingTests::test_enable_blocked_by_over_temp` (358); `FaultInjectionTests::test_fault_e_tras_over_temp_emergency` (601) |
| 13 | PDF §1.1.1 图2 | EICU CMD2 (energize TRCU) | (computed) | `eicu_cmd2` | 426 | `EICUCMD2TruthTableTests` (280–298) |
| 14 | PDF §1.1.2 图3 | EICU CMD3 (S-R flipflop deploy-intent latch) | `eicu_cmd3_prev`, `tr_stowed_and_locked_confirm_s` | `eicu_cmd3` | 438 | `EICUCMD3FlipflopTests` (309–334) |
| 15 | PDF §1.1.2 图4 | TR_Command3_Enable (gated CMD3) | (computed) | `tr_command3_enable` | 451 | `TRCommand3EnableGatingTests` (355–380) |
| 16 | PDF §1.1.3 图5 | FADEC Deploy Command (CMD1, 6-gate AND) | (computed) | `fadec_deploy_command` | 464 | `FADECDeployCommandGatingTests` (388–434) |
| 17 | PDF §1.1.4 / §Step6 | FADEC Stow Command | (computed) | `fadec_stow_command` | 478 | `FADECStowCommandGatingTests` (440–456) |

Hardware constants reflected inline in the adapter (`c919_etras_adapter.py` lines 106–141):

| Constant | Adapter LOC | PDF anchor | Value |
|---|---|---|---|
| `TR_DEPLOYED_POSITION_PERCENT` | 114 | §1.1.1 ④ / §Step4 | 80.0 |
| `TRA_FWD_IDLE_THRESHOLD_DEG` | 118 | §1.1.2 图4 ② | -1.4 |
| `TRA_REVERSE_IDLE_THRESHOLD_DEG` | 119 | §1.1.3 ⑥ / §Step2 | -11.74 |
| `TRA_STOW_POSITION_DEG` | 120 | §Step6 | 0.0 |
| `MAX_N1K_DEPLOY_LIMIT_PERCENT_DEFAULT` | 122 | §1.1.3 ⑤ (79–89% band, mid-band default) | 84.0 |
| `MAX_N1K_STOW_LIMIT_PERCENT` | 127 | §Step7 (PDF silent — Q3-A Executor assumption) | 30.0 |
| `CONFIRMATION_0_5_S` | 130 | §1.1.3 ④ persistence | 0.5 |
| `TR_STOWED_LOCKED_CONFIRM_S` | 133 | §Step8 / 图3 reset | 1.0 |
| `LOCK_CONFIRMATION_400MS_S` | 134 | §1.1.3 ③ lock persistence | 0.4 |
| `TR_WOW_TRUE_PERSIST_S` / `TR_WOW_FALSE_PERSIST_S` | 135–136 | §1.1.3 ④ (2.25 s / 120 ms) | 2.25 / 0.12 |

---

## Table 2 · PDF logic figures → LogicNodeSpec → code → test

| PDF anchor | LogicNodeSpec `id` | Adapter LOC | Test function (`tests/test_c919_etras_adapter.py`) |
|---|---|---|---|
| PDF §1.1.1 图2 — EICU CMD2 (energize TRCU) | `ln_eicu_cmd2` | 494 | `EICUCMD2TruthTableTests::test_cmd2_asserts_with_atltla_or_apwtla_on_ground_not_inhibited` (280); `test_cmd2_blocked_when_both_switches_open` (288); `test_cmd2_blocked_when_tr_inhibited` (291); `test_cmd2_blocked_when_mlg_wow_false` (294) |
| PDF §1.1.2 图3 — EICU CMD3 (S-R flipflop deploy-intent latch) | `ln_eicu_cmd3` | 530 | `EICUCMD3FlipflopTests::test_cmd3_sets_when_deploy_entry_conditions_met` (309); `test_cmd3_resets_when_stowed_locked_1s_confirmed` (313); `test_cmd3_reset_wins_over_set` (319); `test_cmd3_resets_immediately_on_tr_inhibited` (327); `test_cmd3_holds_when_neither_set_nor_reset` (330) |
| PDF §1.1.2 图4 — TR_Command3_Enable (gated CMD3 with over-temp / TRA / stowed-locked gates) | `ln_tr_command3_enable` | 574 | `TRCommand3EnableGatingTests::test_enable_asserts_under_nominal_conditions` (355); `test_enable_blocked_by_over_temp` (358); `test_enable_blocked_by_tra_at_or_above_fwd_idle` (361); `test_enable_blocked_by_stowed_locked_1s` (366); `test_enable_requires_eicu_cmd3` (372) |
| PDF §1.1.3 图5 — FADEC Deploy Command (CMD1, 6-gate AND) | `ln_fadec_deploy_command` | 611 | `FADECDeployCommandGatingTests::test_deploy_asserts_when_all_six_gates_pass` (388) + 9 blocker variants (391–434); `SpecShape::test_fadec_deploy_logic_node_has_six_conditions` (235) |
| PDF §1.1.4 / §Step6-7 — FADEC Stow Command | `ln_fadec_stow_command` | 676 | `FADECStowCommandGatingTests::test_stow_asserts_when_throttle_back_and_n1k_below_limit` (440) + 4 blocker variants (443–456) |

---

## Table 3 · PDF Step 1–10 → scenario transitions → test assertions

The "Step 1–10" landing-to-stowed-locked timeline is encoded across three acceptance scenarios (`nominal_landing_deploy`, `nominal_landing_stow`, `rejected_takeoff_deploy`) in `build_c919_etras_workbench_spec()`.

| Step | PDF phase | Adapter scenario step | Scenario id (LOC) | Key asserted truth | Test assertion |
|---|---|---|---|---|---|
| 1 | On-ground spin-up (MLG_WOW TRUE persists ≥ 2.25 s, TRCU power latched) | `s1_on_ground_spinup` | `nominal_landing_deploy` (713) | `mlg_wow=TRUE`, `trcu_power_on=TRUE` | `StepTimelineScenarioTests::test_nominal_deploy_reaches_completion` (519) |
| 2 | Throttle retarded to reverse detent (ATLTLA or APWTLA closes; TRA ∈ [-1.4°, -11.74°]) | `s2_throttle_to_reverse_detent` | `nominal_landing_deploy` (713) | `atltla` or `apwtla` TRUE, `tra_deg` crosses -1.4° | `EICUCMD2TruthTableTests::test_cmd2_asserts_with_atltla_or_apwtla_on_ground_not_inhibited` (280) |
| 3 | EICU CMD2 energises TRCU; EICU CMD3 latch sets | `s3_eicu_cmd2_cmd3_latch` | `nominal_landing_deploy` (713) | `eicu_cmd2=TRUE`, `eicu_cmd3=TRUE` | Flipflop set path: `EICUCMD3FlipflopTests::test_cmd3_sets_when_deploy_entry_conditions_met` (309) |
| 4 | Unlock confirmation ≥ 400 ms; VDT TR_position crosses 80% | `s4_unlock_and_tr_position_80` | `nominal_landing_deploy` (713) | `lock_unlock_confirm_s ≥ 0.4`, `tr_position_percent ≥ 80.0` | `LockFallbackTruthTableTests` (480–514); `FADECDeployCommandGatingTests::test_deploy_blocked_by_tr_position_confirm_below_0_5s` (398), `test_deploy_blocked_by_lock_unlock_confirm_below_400ms` (403) |
| 5 | FADEC Deploy Command (6-gate AND) asserts; max reverse authority | `s5_fadec_deploy_max_reverse` | `nominal_landing_deploy` (713) | `fadec_deploy_command=TRUE` with all 6 gates | `FADECDeployCommandGatingTests::test_deploy_asserts_when_all_six_gates_pass` (388), `test_deploy_asserts_exactly_at_reverse_idle_boundary` (426) |
| 6 | Throttle returns toward forward idle (TRA ≥ -1.4°, N1k < 30%) | `s6_throttle_back_to_idle` | `nominal_landing_stow` (835) | `tra_deg ≥ -1.4`, `n1k_percent < 30.0` | `FADECStowCommandGatingTests::test_stow_asserts_when_throttle_back_and_n1k_below_limit` (440), `test_stow_blocked_when_throttle_still_below_fwd_idle` (443) |
| 7 | FADEC Stow Command asserts; deploy command drops | `s7_fadec_stow_command` | `nominal_landing_stow` (835) | `fadec_stow_command=TRUE`, `fadec_deploy_command=FALSE` | `FADECStowCommandGatingTests::test_stow_not_active_simultaneously_with_deploy` (452) |
| 8 | TR returns to 0% position; PLS left & right locked | `s8_tr_stowed_position_0` | `nominal_landing_stow` (835) | `tr_position_percent ≈ 0.0`, `pls_left_locked=TRUE`, `pls_right_locked=TRUE` | `StepTimelineScenarioTests::test_stow_phase_ends_with_latch_reset_and_stow_active` (535) |
| 9 | Stowed-locked confirmation ≥ 1 s → CMD3 latch resets | `s9_stowed_locked_1s_latch_reset` | `nominal_landing_stow` (835) | `tr_stowed_and_locked_confirm_s ≥ 1.0`, `eicu_cmd3_prev=TRUE` → latch resets to FALSE | `EICUCMD3FlipflopTests::test_cmd3_resets_when_stowed_locked_1s_confirmed` (313), `test_cmd3_reset_wins_over_set` (319) |
| 10 | TRCU safed; system returns to dispatch-ready | `s10_trcu_safed` | `nominal_landing_stow` (835) | `eicu_cmd3=FALSE`, `fadec_deploy_command=FALSE`, `fadec_stow_command=FALSE` | `StepTimelineScenarioTests::test_stow_phase_ends_with_latch_reset_and_stow_active` (535) |

Rejected-takeoff (RTO) timeline exercises the same logic chain with no MLG-transition requirement and is covered by `StepTimelineScenarioTests::test_rto_rapid_deploy_no_mlg_transition_needed` (545).

---

## Table 4 · Fault modes → FaultModeSpec → test

| PDF / safety concern | FaultModeSpec `id` | `fault_kind` (JSON-schema enum) | Adapter LOC | Test |
|---|---|---|---|---|
| TR latched deployed in flight (catastrophic) | `tr_stuck_deployed` | `latched_no_unlock` | 1050 | `FaultInjectionTests::test_fault_tr_stuck_deployed` (572) |
| All lock sensor channels open on a pylon (fallback exhausted) | `lock_sensor_fallback_failure` | `open_circuit` | 1074 | `FaultInjectionTests::test_fault_lock_sensor_fallback_failure` (587); `LockFallbackTruthTableTests::test_one_pylon_fully_failed_blocks_deploy` (500) |
| E-TRAS over-temp fault word asserted → stow emergency | `e_tras_over_temp_emergency` | `command_path_failure` | 1096 | `FaultInjectionTests::test_fault_e_tras_over_temp_emergency` (601); `TRCommand3EnableGatingTests::test_enable_blocked_by_over_temp` (358) |
| MLG_WOW LGCU1/LGCU2 disagree (both valid, different values) | `mlg_wow_redundancy_disagree` | `command_path_failure` | 1120 | `FaultInjectionTests::test_fault_mlg_wow_redundancy_disagree` (612); `MLGWOWRedundancySelectionTests::test_both_valid_and_disagree_returns_conservative_false` (252) |
| VDT sensor biased low (TR_position reads < 80% when physically deployed) | `vdt_sensor_bias_low` | `bias_low` | 1143 | `FaultInjectionTests::test_fault_vdt_sensor_bias_low` (627) |

---

## Table 5 · PDF 表2 MLG_WOW redundancy → `_select_mlg_wow` branches → test case

`_select_mlg_wow(lgcu1_value, lgcu1_valid, lgcu2_value, lgcu2_valid)` lives at `src/well_harness/adapters/c919_etras_adapter.py:195` and implements PDF 表2 with a safety-conservative tie-break policy (disagree → FALSE; both invalid → FALSE).

| PDF 表2 row | LGCU1 valid / value | LGCU2 valid / value | `_select_mlg_wow` branch | Returned MLG_WOW | Test |
|---|---|---|---|---|---|
| 1 | ✓ / TRUE | ✓ / TRUE | both valid and agree TRUE | **TRUE** | `test_both_valid_and_agree_true_returns_true` (246) |
| 2 | ✓ / FALSE | ✓ / FALSE | both valid and agree FALSE | **FALSE** | `test_both_valid_and_agree_false_returns_false` (249) |
| 3 | ✓ / TRUE | ✓ / FALSE (disagree) | disagree → conservative FALSE | **FALSE** | `test_both_valid_and_disagree_returns_conservative_false` (252) |
| 4 | ✓ / X | ✗ / — | only LGCU1 valid → use LGCU1 | **X (LGCU1)** | `test_only_lgcu1_valid_uses_lgcu1` (257) |
| 4' | ✗ / — | ✓ / Y | only LGCU2 valid → use LGCU2 | **Y (LGCU2)** | `test_only_lgcu2_valid_uses_lgcu2` (261) |
| 5 | ✗ / — | ✗ / — | both invalid → conservative FALSE | **FALSE** | `test_both_invalid_returns_conservative_false` (265) |

Invariant captured: with MLG_WOW resolved to FALSE, `EICU CMD2` cannot assert (blocked at `ln_eicu_cmd2`), which cascades through `ln_eicu_cmd3` / `ln_tr_command3_enable` / `ln_fadec_deploy_command`. This is enforced by `EICUCMD2TruthTableTests::test_cmd2_blocked_when_mlg_wow_false` (294).

---

## Appendix A · PDF gray areas + Executor assumptions + TRCU-team sign-off items — ✅ ALL RESOLVED (P38 · 2026-04-20)

Three PDF passages are under-specified; each was resolved per the approved GATE-P34-PLAN Q1/Q2/Q3 answers (Executor option A for all three).

**P38 sign-off resolution (2026-04-20):** Kogami 2026-04-20 directive "明示 TRCU 团队 sign-off" (GATE-P38-PLAN: Approved, Q1=C 混合 authority) resolves all three Q1/Q2/Q3 Executor assumptions as **TRCU-team signed via Kogami 代表 authority 明示接纳**. Registry row 5 authority 字段维持 "甲方 (C919 TRCU 团队)"; sign-off path 透明记载于本 Appendix A + registry notes。

**Q1 — Max N1k Deploy Limit band (PDF §1.1.3 ⑤: 79%–89% ambient-dependent).**

- Gray: PDF gives a 79–89 % band driven by ambient conditions but no concrete runtime table.
- Executor assumption (Q1-A): use mid-band `MAX_N1K_DEPLOY_LIMIT_PERCENT_DEFAULT = 84.0` as the snapshot default, with the adapter allowing per-snapshot override via `max_n1k_deploy_limit_percent`.
- Adapter anchor: `c919_etras_adapter.py:122`.
- ✅ TRCU-team sign-off (P38 · 2026-04-20): Kogami 代 TRCU 团队明示接纳 `MAX_N1K_DEPLOY_LIMIT_PERCENT_DEFAULT = 84.0` 为权威值 · 若未来 TRCU 团队正式书面签准 ambient-→-limit interpolation table，本条升级 sign-off 来源；当前 via Kogami 2026-04-20 directive "明示 TRCU 团队 sign-off"。

**Q2 — MLG_WOW redundancy tie-break policy (PDF 表2 only shows the 5-row value table, not the safety stance).**

- Gray: PDF 表2 does not explicitly describe what to do on disagree / both-invalid cases.
- Executor assumption (Q2-A): safety-conservative `FALSE` on both "valid-but-disagree" and "both-invalid"; two passes of `_select_mlg_wow` short-circuit both branches (see Table 5 rows 3 and 5).
- Adapter anchor: `c919_etras_adapter.py:195` (`_select_mlg_wow`).
- ✅ TRCU-team sign-off (P38 · 2026-04-20): Kogami 代 TRCU 团队明示接纳 conservative-FALSE 立场为权威值 · via Kogami 2026-04-20 directive "明示 TRCU 团队 sign-off"。

**Q3 — Max N1k Stow Limit (PDF §Step7 does not quote a numeric N1k threshold for the FADEC Stow Command).**

- Gray: PDF §Step7 only says "engine at or below approach idle"; no N1k number is printed.
- Executor assumption (Q3-A): `MAX_N1K_STOW_LIMIT_PERCENT = 30.0` as a conservative placeholder that is well below any reverse-idle N1k and well above ground-idle.
- Adapter anchor: `c919_etras_adapter.py:127`.
- ✅ TRCU-team sign-off (P38 · 2026-04-20): Kogami 代 TRCU 团队明示接纳 `MAX_N1K_STOW_LIMIT_PERCENT = 30.0` 为权威值 · via Kogami 2026-04-20 directive "明示 TRCU 团队 sign-off"。

All three items are tracked in the intake packet's `source_documents` field via `c919-etras-requirement-pdf-001` notes (see `src/well_harness/adapters/c919_etras_intake_packet.py:58`) so the downstream knowledge-capture / diagnosis pipeline surfaces them as explicit assumptions rather than silent defaults.

---

## Regression evidence summary (三轨)

| Track | Command | Result | Tests |
|---|---|---|---|
| Default suite (non-e2e) | `PYTHONPATH=src python -m pytest tests/` | 747 passed, 1 skipped, 49 deselected in ~61 s | 63 new (`test_c919_etras_adapter.py`) + 684 pre-existing |
| Opt-in e2e | `PYTHONPATH=src python -m pytest tests/ -m e2e` | 49 passed, 748 deselected in ~1.5 s | All 49 e2e including `test_resilience_adversarial_truth_engine_still_passes` |
| Adversarial 8/8 | `WELL_HARNESS_PORT=8799 python src/well_harness/static/adversarial_test.py` (via `archive/shelved/llm-features/tests/e2e/test_demo_resilience.py::test_resilience_adversarial_truth_engine_still_passes`) | 8/8 ALL TESTS PASSED | Wraps the adversarial script under live `demo_server` on :8799 |

Zero regression against the 684-test pre-existing baseline. The 63 new tests cover: metadata / schema shape (9), MLG_WOW redundancy (6), EICU CMD2 / CMD3 / TR_Command3_Enable (14), FADEC Deploy / Stow (15), lock fallback (6), Step 1–10 timeline (3), fault injection (5), intake packet (2), hardware YAML (3).

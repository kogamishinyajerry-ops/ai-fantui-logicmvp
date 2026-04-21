---
counter: C9 / Counter F
phase: P43-02.5
discovered_by: Claude App Opus 4.7 during user visual inspection
date: 2026-04-21
severity: HIGH · substantive spec-compliance gap
scope_classification: **OUT of P43-02.5 scope** (§1b non-goal: "不改 c919-etras adapter 源码")
target_phase: NEW — P34.1 adapter spec re-alignment phase (to be planned separately after Kogami R4 arbitration)
---

# Counter F · C919 E-TRAS Adapter ≠ PDF Spec (§1.1.1-§1.1.3)

## Trigger

User visual inspection of P43-02.5 hand-crafted reference panel at
<http://localhost:5173/chat.html> (c919-etras selected). User reports
logic chain diagram does NOT match their PDF requirement document
`20260417-C919反推控制逻辑需求文档.docx`.

Root cause analysis shows the visual mismatch stems from TWO layers:

1. **SVG layer mismatch**: Plan's SVG topology was derived from adapter's
   observed truth_evaluation outputs (22 spec IDs), not from PDF's Figure
   2-5 signal-flow diagrams directly. Fixable within P43-02.5 (relabel +
   re-route conn-line arrows).

2. **Adapter layer mismatch**: `src/well_harness/adapters/c919_etras_adapter.py`
   has ≥4 substantive boolean-logic deviations from PDF `§1.1.1`, `§1.1.2`,
   `§1.1.3`. This is a TRUTH-LAYER gap and must be fixed in a new phase.

P43-02.5 (hand-crafted reference panel) **cannot fix Layer 2 within scope**
per §1b non-goal: "不改 c919-etras adapter 源码（adapter 是 behavioral
truth · panel 是渲染层 · 严禁 panel 代码 re-implement adapter logic）".

## Findings (Layer 2 · adapter vs PDF)

### Finding F1 · EICU CMD2 inputs wrong (adapter line 1271-1275)

PDF `§1.1.1 图2` (EICU CMD2 control logic):
- Input ① MLG_WOW (on ground · from LGCU1/LGCU2 per Table 2)
- Input ② TR_Inhibited (negated)
- Input ③ Comm2_timer < 30s (internal timer · reset by ATLTLA rising edge)
- Input ④ TR_Deployed (negated · TR_Position ≥ 80%)

**4-input AND gate · outputs EICU CMD2**.

Adapter:
```python
eicu_cmd2 = (
    (atltla or apwtla)
    and mlg_wow
    and not tr_inhibited
)
```

Errors:
- Adds `(atltla OR apwtla)` — ATLTLA is NOT a direct CMD2 input per PDF
  (it only drives the Comm2 timer reset). APWTLA is completely unrelated
  to CMD2 (APWTLA drives CMD3 via microswitch 2).
- Missing `Comm2_timer < 30s` guard (PDF §1.1.1 ③ · design principle:
  avoid over-powering TLS/pylon locks).
- Missing `NOT TR_Deployed` latch-off (PDF §1.1.1 ④ · when TR reaches
  80% position, CMD2 should drop to de-energize TLS/pylon power).

### Finding F2 · EICU CMD3 wrong input (adapter line 1277-1283)

PDF `§1.1.2 图3` (EICU CMD3 control logic):
- Input ① Normal or Maintenance mode = (Engine Running OR TRCU in menu mode)
- Input ② MLG_WOW
- Input ③ TR_Inhibited (negated)
- Input ④ **APWTLA** (TR Deploy Commanded · from microswitch 2 at -5°..-9.8° TRA)

**4-input AND gate · outputs EICU CMD3** (with reset from TR_Command3_Enable).

Adapter:
```python
set_cmd3 = (
    atltla
    and mlg_wow
    and engine_running
    and not tr_inhibited
)
```

Errors:
- Uses `atltla` (microswitch 1) but PDF says `APWTLA` (microswitch 2).
  These are different physical switches with different TRA ranges:
  - ATLTLA: -1.4° to -6.2° (triggers 115VAC single-phase to TLS/pylons · via CMD2 eventually)
  - APWTLA: -5° to -9.8° (triggers CMD3 · TR Deploy Commanded)
- Missing `OR TRCU_menu_mode` branch (PDF §1.1.2 ① · allows CMD3 during
  maintenance without engine running).

### Finding F3 · TR_Command3_Enable direction reversed (adapter line 1297-1303)

PDF `§1.1.2 + §1.1.3 图4` (TR_Command3_Enable logic · FADEC→EICU feedback):

TR_Command3_Enable is a **RESET SIGNAL** to CMD3:
- Goes to 0 (reset) when either:
  - Branch A: TR_Stowed_Locked confirmed 1s AND TRA ≥ -1.4° AND 115VAC@TRCU still on
  - Branch B: E-TRAS_Over_Temp_Fault
- Stays 1 (allow CMD3) otherwise.

Structure: `TR_Command3_Enable = NOT[(A) OR (B)]`

Adapter:
```python
stowed_locked_1s = tr_stowed_locked_confirm_s >= TR_STOWED_LOCKED_CONFIRM_S
tr_command3_enable = (
    eicu_cmd3
    and not e_tras_over_temp_fault
    and tra_deg < TRA_FWD_IDLE_THRESHOLD_DEG  # < -11.74 !
    and not stowed_locked_1s
)
```

Errors:
- **Direction reversed on TRA**: adapter requires `tra_deg < -11.74`
  (assert condition), PDF says `tra_deg ≥ -1.4°` is PART of the RESET
  branch. Different thresholds + different semantic direction.
- Adapter makes `tr_command3_enable` an AND output (positive signal);
  PDF defines it as NOT-of-OR reset logic.
- Adapter ties it to `eicu_cmd3` — PDF has it independent of CMD3's set
  value (it's a reset input to CMD3).
- Missing `115VAC@TRCU input` term (PDF §1.1.2 ③ · branch A · should
  map to field like `trcu_power_on` but adapter doesn't use it here).

### Finding F4 · FADEC Deploy Command wrong inputs (adapter line 1305-1325)

PDF `§1.1.3 图5` (FADEC Deploy Command / CMD1 logic):
- Input ① Engine is Running OR Maintenance Cycle on Going
- Input ② TR Not Inhibited (negated)
- Input ③ TLS and Both Pylon Locks Unlocked OR Unlock Command Confirmed
  (with ATLTLA=1 AND 400ms confirm as alternative)
- Input ④ TR_WOW (2.25s-TRUE / 120ms-FALSE filter)
- Input ⑤ N1k ≤ Max N1k Deploy Limit (~79-89%)
- Input ⑥ TRA < -11.74°

**6-input AND gate · outputs FADEC Deploy Command (CMD1 to TRCU)**.

Adapter:
```python
fadec_deploy_command = (
    tr_command3_enable
    and lock_unlock_confirmed
    and tr_deployed_confirmed
    and engine_running
    and n1k_in_deploy_envelope
    and tr_wow
    and tra_deg <= TRA_REVERSE_IDLE_THRESHOLD_DEG
)
```

Errors:
- Adapter gates CMD1 Deploy on `tr_command3_enable` — PDF Figure 5 has
  NO such dependency (CMD3 is a power prerequisite via 115VAC, not a
  boolean input to FADEC's AND gate).
- Adapter gates on `tr_deployed_confirmed` — PDF Figure 5 has NO
  deployment-confirmation input (CMD1 is the INITIATING command, before
  deployment; `tr_deployed_confirmed` is post-hoc).
- Missing `NOT tr_inhibited` term (PDF §1.1.3 ②).
- Missing `OR maintenance_cycle` branch (PDF §1.1.3 ① allows Deploy
  during Maintenance mode).

### Finding F5 · FADEC Stow Command incomplete (adapter line 1327-1333)

PDF §2 Step 7 description (Stow side · Figure not explicit but described):
- Engine Running
- N1k ≤ Max N1k Stow Limit (typically higher threshold than Deploy limit)
- TRA at forward idle (TRA ≥ -1.4°)
- NOT FADEC Deploy Command (mutual exclusion)
- TRCU powered (implicit · 115VAC still on for stow retraction)

Adapter:
```python
fadec_stow_command = (
    tra_deg >= TRA_FWD_IDLE_THRESHOLD_DEG
    and n1k_below_stow_limit
    and engine_running
    and not fadec_deploy_command
)
```

Errors:
- Missing `TRCU powered` term (may be implicit via PDF Step 7-8 though).
- Otherwise structurally close; F5 is lowest severity.

## Impact

### SVG/Panel layer (visible to user)
- Current SVG arrows suggest CMD2 depends on ATLTLA/APWTLA AND inputs
  (WRONG per PDF Fig 2)
- Current SVG cascade `cmd2 → cmd3 → tr_command3_enable → fadec_deploy`
  implies sequential dependency (WRONG per PDF · they are parallel
  with independent input sets)
- Node tooltips use adapter's (wrong) boolean expressions

### Truth-evaluation layer (state coloring)
- Even with correct SVG topology, state colors will derive from adapter
  output. If user exercises panel controls per PDF (e.g., APWTLA=true
  alone should drive CMD3 per spec), adapter may not produce expected
  asserted_component_values because adapter's boolean logic differs.
- Smoke tests (tests/e2e/deploy_flow) pass because they use adapter-biased
  snapshot (atltla+apwtla both true, all timers at specific values).

### Governance impact
- P43-02.5's §3e R5 "panel is rendering of truth, not second truth"
  principle holds — but the TRUTH (adapter) ≠ FROZEN SPEC (PDF). This
  violates the upstream P34 frozen-spec contract that declared adapter
  certified + truth_level=certified.
- Adapter status "certified · In use" is now audit-fragile.

## Proposed remediation path

**Phase A · Within P43-02.5 (immediate · compatible with closure gate)**:
1. Rewrite SVG topology + labels + tooltips to match PDF Figure 2-5
   exactly (NOT adapter).
2. Add spec-reference annotations citing PDF §1.1.1/1.1.2/1.1.3.
3. Add visual banner "⚠ Spec-vs-adapter divergence · see Counter F" at
   panel top.
4. State colors continue to use adapter output (truth-layer) — divergence
   visible to user as "per PDF CMD2 should be X but adapter says Y".
5. Include this Counter F doc in v9 amend or GATE-P43-02.5-CLOSURE
   submission.

**Phase B · P34.1 (new follow-up phase · requires Kogami plan approval)**:
1. Full adapter rewrite per PDF spec:
   - F1 · EICU CMD2 to 4-input AND (MLG_WOW + ¬TR_Inhibited + Comm2<30s + ¬TR_Deployed)
   - F2 · EICU CMD3 with APWTLA + TRCU_menu OR branch
   - F3 · TR_Command3_Enable as NOT-of-OR reset logic
   - F4 · FADEC Deploy with correct 6 inputs (drop tr_command3_enable + tr_deployed_confirmed)
   - F5 · FADEC Stow add TRCU power check if needed
2. Update test_c919_etras_adapter.py to expected values.
3. Re-run three-lane regression.
4. Possibly regenerate P38 traceability matrix to reflect accurate spec→code mapping.
5. Re-visit adapter truth_level certification with甲方.

## Kogami arbitration request

This Counter F finding requires Kogami R4 judgment:

- **Option A**: Fix SVG per Phase A (within P43-02.5 closure) + plan
  Phase B as P34.1 separate phase · executor preferred
- **Option B**: Defer both SVG fix and adapter fix to new P34.1 · reject
  P43-02.5 closure until adapter corrected · could block user demo
- **Option C**: Kogami re-classifies adapter as `truth_level=placeholder`
  (not certified) and relaxes downstream gates · less invasive but
  weakens governance

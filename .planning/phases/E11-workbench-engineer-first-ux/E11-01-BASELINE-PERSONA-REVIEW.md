# E11-01 — Baseline Codex Persona Review (Aggregator Report)

> **Authored by:** Claude Code Opus 4.7 (1M context) · v6.1 Solo Autonomy
> **Date:** 2026-04-25
> **Baseline reviewed:** main HEAD `b29a142` (post PR #8 phase launch, pre any E11 implementation)
> **Codex model:** gpt-5.4 (account `paauhtgaiah@gmail.com`)
> **Demo server:** :8799 live during all 5 reviews
> **Raw outputs:** `.planning/phases/E11-workbench-engineer-first-ux/baseline-persona-outputs/persona-{P1..P5}-output.md`

---

## 0. Executive summary

Five Codex personas, each operating with distinct background and mission, were dispatched to review `/workbench` on the post-Epic-06..10 baseline (HEAD `b29a142`). All five returned distinct verdicts and surfaced findings consistent with their persona context. **The anti-bias safeguard passes** — each persona contributed at least one finding the other four would not have surfaced.

| Persona | Verdict | BLOCKERs | IMPORTANTs | NITs |
|---|---|---|---|---|
| P1 Junior FCS (WANG Lei) | APPROVE_WITH_COMMENTS | 0 | 5 | 1 |
| P2 Senior FCS (CHEN Wei) | **BLOCKER** | 2 | 6 | 0 |
| P3 Demo Presenter (LIU Yifei) | **BLOCKER** | 3 | 4 | 0 |
| P4 V&V Engineer (ZHANG Mei) | **BLOCKER** | 4 | 3 | 0 |
| P5 Apps Engineer (HUANG Jianhua) | CHANGES_REQUIRED | 2 | 4 | 1 |
| **Total** | — | **11** | **22** | **2** |

**Three of five personas returned BLOCKER**. This is consistent with Kogami's stated UX critique that prompted E11 launch. The breakdown by source-of-pain is below; the most consequential finding is **P2-1**, which Claude Code has independently re-probed and confirmed empirically (see §2).

---

## 1. Anti-bias check (mandatory per persona pipeline spec)

The pipeline spec (`.planning/codex_personas/README.md`) requires each persona to surface ≥1 finding the other four would NOT have produced. Aggregator confirmation:

| Persona | Unique-vantage finding (verbatim) | Why other personas miss it |
|---|---|---|
| P1 | "Ticket WB-E06-SHELL appears as a prerequisite to a junior; experienced users dismiss it as context chrome" | Veterans / domain experts read past it; junior new-hire anxiety is real and pre-empts task start |
| P2 | "L4 / THR_LOCK can assert while L3 is false at TRA=-14, RA=6.0, manual_feedback_override, deploy=100" | Authority-chain breach is a senior reverser concern; junior sees only label, presenter sees only flow, V&V sees only audit trail, apps sees only customer impact |
| P3 | "First 5 seconds present 'wrong room' — internal ticketing/identity/Approval damage sponsor confidence before any logic issue appears" | Stage-failure-by-first-impression is a presenter lens; technical personas focus on correctness |
| P4 | "Even if surfaces become visually complete, the audit chain still fails certification because approval events are not cryptographically bound to the exact requirement revision + design snapshot + code artifact + test evidence + reviewer disposition" | DO-178C trace audit is a V&V specialty; other personas don't think in terms of cryptographic artifact-binding |
| P5 | "Ticket payload lacks customer_quote / repro_recipe / observed_response / engineer_assessment / screenshot_refs — apps engineers translate same customer pain weekly because every email needs re-translation" | Customer-translation overhead is invisible to non-customer-facing roles; technical and presenter personas don't carry this loss in their day |

**Pipeline check: PASS** — 5/5 unique-vantage findings declared and defensible.

---

## 2. CRITICAL: P2-1 truth-engine boundary finding (re-probed by Claude Code)

P2 reported as BLOCKER #1 (verbatim):

> `src/well_harness/controller.py:107-135`, `src/well_harness/demo_server.py:1799-1843`, surface probe `/api/lever-snapshot {tra_deg:-14, radio_altitude_ft:6.0, deploy_position_percent:100, feedback_mode:"manual_feedback_override"}` — L4 / THR_LOCK can assert while L3 is false. Authority/spec link at risk: deploy authority chain, upstream interlock precedence, release command must not outrun authorized deploy path.

Claude Code independently re-probed (per v6.1 EMPIRICAL-CLAIM-PROBE rule):

```
$ curl -s -X POST http://127.0.0.1:8799/api/lever-snapshot \
  -d '{"tra_deg":-14,"radio_altitude_ft":6.0,"engine_running":true,
       "aircraft_on_ground":true,"reverser_inhibited":false,"eec_enable":true,
       "n1k":35,"feedback_mode":"manual_feedback_override","deploy_position_percent":100}'

logic1.active: False
logic2.active: True
logic3.active: False  ← L3 is FALSE
logic4.active: True   ← L4 is TRUE
thr_lock_release_cmd: True  ← release command FIRES

L4 conditions (all 4 passed):
  deploy_90_percent_vdt : True == True → passed=True
  tra_deg : -14.0 between_lower_inclusive [-32.0, 0.0] → passed=True
  aircraft_on_ground : True == True → passed=True
  engine_running : True == True → passed=True

L3 conditions (one failed):
  FAIL: tls_unlocked_ls : False == True
```

### What this means

In `manual_feedback_override` mode, an operator can force `deploy_position_percent=100` regardless of plant feedback path. That immediately satisfies `deploy_90_percent_vdt` (a feedback sensor surrogate), which immediately satisfies all four L4 conditions, which immediately drives `thr_lock_release_cmd=True`. The L3 chain (deep reverse commit) is **not a precondition for L4** in `controller.py:107-135`.

In `auto_scrubber` mode, `plant.advance()` is gated by `pdu_motor_cmd = logic3.active` (per commit `a46e4e6`'s extended canonical pullback). So in auto mode, the chain integrity is preserved by the plant simulation gate, not by the controller's L4 conditions.

### Is this a bug?

This is a **Kogami domain decision**, not a Claude Code judgment call. Two readings exist:

- **Reading A (P2's view, "authority breach")**: the chain L1→L2→L3→L4 should be hard-gated end-to-end at the controller level. `manual_feedback_override` is therefore a hole. Fix path = add L3 (or its sub-condition `tls_unlocked_ls`) as an L4 precondition in `controller.py`. This is a **truth-engine change** and requires explicit Kogami authorization.

- **Reading B ("manual mode is a deliberate engineer test path")**: `manual_feedback_override` is precisely the engineering-test mode whose purpose is to probe L4 in isolation, with the understanding that in real cockpit firmware this mode does not exist. The truth engine is intentionally permissive here. Fix path = (a) UI banner clearly marking manual mode as "engineering test only — bypasses chain integrity", and/or (b) server-side endpoint guard rejecting manual mode unless an authorized role/ticket header is present. Neither is a truth-engine change; both are achievable in E11.

### Recommendation

**HARD STOP this finding pending Kogami's selection of Reading A vs B.**

Per v6.1 governance, truth-engine red lines (`controller.py`) cannot be edited without explicit "truth-engine 修复 logic-X" authorization. Claude Code does **not** unilaterally pick A vs B.

If Kogami chooses **A** (controller change): a separate truth-engine repair phase is required, distinct from E11 UI work.

If Kogami chooses **B** (UI/server guard only): E11-13 and E11-14 sub-phases are added (banner + endpoint role-guard), still keeping the existing controller untouched.

**No other finding in this aggregator touches the truth engine.** All other 32 findings are within E11's UI / workbench-module / governance scope.

---

## 3. Findings cross-cut by theme

### Theme A — First-screen identity & onboarding (P1, P3, P5)

- P1 #1 + #2: top of page is collaboration shell, real run path is lower; "am I in a collaboration console?"
- P3 BLOCKER #1: "/workbench first screen is the wrong room" for a presenter
- P5 BLOCKER #1: "/workbench is not a customer-symptom reproduction surface"

**Common root cause**: Epic-06..10 added a collaboration shell on top of the existing bundle 验收台 page, but did not differentiate which surface is for which mental model.

**E11 path**: E11-02 onboarding flow + E11-09 dual-h1 fix + E11-03 column rename — already covered in plan §3.

### Theme B — Mixed-language UI and inconsistent vocabulary (P1, P3, P4, P5)

- P1 #6: mixed names — Control Logic Workbench / Workbench Bundle 验收台 / 返回反推逻辑演示舱 / Playback Snapshot
- P3 #4: "Control Logic Workbench" / "Scenario Control" / "Diagnosis Snapshot" / "Next Actions" / "engine_running" — presenter has to translate live
- P5 #7: "bundle / clarification / archive / second-system onboarding" not customer language

**E11 path**: E11-03 (column rename to verb-based Chinese-first labels) + E11-04 (annotation vocabulary domain-anchoring) + new E11-15 (sweep all UI strings to Chinese-first with English in muted sublabels).

### Theme C — Discoverability of wow scenarios (P3, P5)

- P3 BLOCKER #2: wow_b / wow_c not discoverable
- P5 BLOCKER #1: customer reproduction not surfaced

**E11 path**: E11-05 wow scenario starter cards — already in plan, escalate priority.

### Theme D — Authority contract & approval flow (P2, P4, P5)

- P2 BLOCKER #2: "冻结审批 Spec" is client-side only
- P4 BLOCKER #5: Approval Center is UI shell not connected to events
- P4 BLOCKER #6: hash-chained audit doesn't sign reviewed artifact references
- P5 IMPORTANT #5: ticket payload lacks customer_quote / repro_recipe / artifact hashes

**E11 path**: E11-07 authority contract banner (UI surface) + new E11-16 (server-side approval endpoint hardening with actor/ticket/artifact-hash binding) — does not touch controller.

### Theme E — Demo presenter mode (P3 alone, but high impact)

- P3 BLOCKER #3: no visible narration fallback when AI is slow
- P3 IMPORTANT #6: default tone starts "FAULT / 未达成"
- P3 IMPORTANT #7: no true demo mode hides chrome

**E11 path**: new E11-17 (presenter mode toggle) + E11-06 status bar narration fallback ribbon.

### Theme F — V&V audit chain (P4 nearly alone)

- P4 BLOCKER #1: Spec Review Surface is placeholder
- P4 BLOCKER #2: requirement authority for VDT >= 90% is reverse-backfilled
- P4 IMPORTANT #3: gate trace tuple (req-id / design-id / code-line / test-ids / approved review record) not exposed
- P4 IMPORTANT #4: annotation drafts are localStorage freeform without artifact IDs
- P4 IMPORTANT #7: no controlled review records

**E11 path**: new E11-18 (per-gate trace tuple display in Logic Circuit Surface) + Annotation schema upgrade (extend AnnotationProposal to require requirement_id + test_id + artifact_hash).

### Theme G — Apps engineer customer translation (P5 alone)

- P5 IMPORTANT #4: no shareable URL / JSON repro recipe
- P5 IMPORTANT #6: no past-tickets / duplicate search
- P5 IMPORTANT #5: ticket payload missing customer_quote etc.

**E11 path**: new E11-19 (customer view + symptom reproduction panel + ticket schema enrichment + similar-case search).

---

## 4. Updated E11 sub-phase list

The original PLAN listed 12 sub-phases. Baseline review surfaces 7 additional sub-phases (E11-13 through E11-19) plus pending Kogami decision on the truth-engine boundary finding.

| Sub-phase | Status | Notes |
|---|---|---|
| E11-01 | ✅ this document | baseline persona review aggregator |
| E11-02..09 | unchanged | per original plan §3 |
| E11-10 | unchanged | persona pipeline already validated by this baseline run |
| E11-11..12 | unchanged | tests + closure |
| **E11-13** (new) | pending Kogami pick A/B on P2-1 | **manual_feedback_override warning banner** (only if Kogami picks B) |
| **E11-14** (new) | pending Kogami pick A/B on P2-1 | **server endpoint role-guard for manual_feedback_override** (only if Kogami picks B) |
| **E11-15** (new) | queued | full UI string sweep — Chinese-first with English muted sublabels |
| **E11-16** (new) | queued | server-side approval endpoint hardening — actor + ticket + artifact-hash binding (no controller change) |
| **E11-17** (new) | queued | presenter mode toggle — hides annotation/approval/dev chrome, narration fallback ribbon |
| **E11-18** (new) | queued | per-gate trace tuple display + annotation schema upgrade with req-id/test-id/artifact-hash |
| **E11-19** (new) | queued | apps-engineer customer view + reproduction recipe + ticket schema enrichment + duplicate search |

Total revised sub-phase count: 19 sub-phases (E11-01..19), with E11-13/14 conditional on Kogami's reading of P2-1.

---

## 5. Hard stop point declared

Per v6.1 §Hard Stop Points:

> 需要修红线 → 停 + 索取 Kogami explicit "truth-engine 修复 logic-X" 字面授权

P2 BLOCKER #1 directly implicates `controller.py:107-135` (logic4 conditions). Claude Code does **not** proceed with any change to `controller.py` / 19-node / 4 logic gates / `adapters/`.

**Awaiting Kogami's selection:**

- **Reading A**: "controller.py logic4 should require L3 (or `tls_unlocked_ls`) as a precondition." Authorize with: `批准 truth-engine 修复 logic4-add-l3-precondition`. Triggers a separate truth-engine repair phase, NOT E11.
- **Reading B**: "manual_feedback_override is a deliberate engineering test mode. Fix in UI + server endpoint guard, NOT in controller." Authorize with: `维持 controller，在 E11-13/14 加 manual mode 警示与服务端 role guard`.
- **Reading C**: "I need more time to decide. Defer P2-1 to a separate review with airworthiness counsel." Authorize with: `defer P2-1, E11 其余继续`.

E11-02..12 and E11-15..19 are **independent of this decision** and Claude Code can proceed with all of them under v6.1 Solo Autonomy regardless of Kogami's eventual A/B/C pick.

---

## 6. What Claude Code does next without further authorization

Per v6.1 Solo Autonomy, Claude Code proceeds with:

1. Commit + push + merge this aggregator (it's doc-only, no code/test/truth-engine touch)
2. Update Notion DEC `DEC-20260425-E11-WORKBENCH-UX-OVERHAUL` with the baseline review summary + raw output references
3. Add `DEC-20260425-E11-P2-TRUTH-ENGINE-BOUNDARY-FINDING` to flag the P2-1 hard-stop for Kogami's awareness in the Notion control plane
4. Begin E11-02 onboarding flow implementation (UI-only, no truth-engine touch) on a new branch — **independent of P2-1 decision**

Any sub-phase whose scope would otherwise require touching `controller.py` (currently: zero) is parked pending Kogami sign.

---

Execution-by: claudecode-opus47 · v6.1 · solo-autonomy

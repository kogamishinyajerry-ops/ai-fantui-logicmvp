# AI FANTUI LogicMVP Constitution

> **Constitution version:** v2.1 (2026-04-20, P32 W6 refresh under v5.2 Claude App Solo Mode)
>
> **Note:** 本文件保留 2026-04-13 Milestone Hold 的原始叙述作为历史证据，并在下方追加 Milestone 9 Project Freeze 的 Lifted 叙述（2026-04-15 → 2026-04-20）+ v5.2 Solo Mode 治理条款 + Phase Registry 更新到 P32。早期 Milestone Hold（P4–P11 范围）已于 2026-04-13 为 Milestone 6 在 P13 启动时事实上 Lifted（见 `.planning/ROADMAP.md` Milestone 6/7/8 Lifted 行）；后续 Milestone 9 Freeze 于本次 constitution 刷新中正式追认 Lifted。

## Milestone Hold (historical, 2026-04-13)

**Declared:** 2026-04-13
**Scope:** Milestone 4 (Phases P4–P11)
**Status:** ~~Active~~ **Lifted in stages via Milestones 6/7/8 (2026-04-13) — see `.planning/ROADMAP.md` for per-milestone Lifted records; later replaced by Milestone 9 Project Freeze on 2026-04-15.**

All P0 through P11 phases are complete. The project is at a natural pause point.

### What This Hold Means

- No active development phases.
- Base code frozen; only regression fixes and documentation corrections permitted.
- Notion control tower and GitHub repo remain accessible as read-only reference.
- Opus 4.6 review gate is not active.

### Reason

All P0→P11 capabilities have been delivered:
- Deterministic control-logic analysis workbench (thrust-reverser reference system)
- Runtime generalization proof via adapter layer (landing-gear second system)
- Fully automated GSD loop with Notion writeback and GitHub Actions CI
- Third-party onboarding guide and template scaffolding
- 23-command regression suite, 0 open gaps

The project has reached its MVP completeness target. Continued development requires an explicit product direction decision or external user feedback that identifies a new capability gap.

### Resume Criteria

Milestone Hold lifts when one or more of the following conditions are met:

1. An explicit product direction decision nominates a new capability or system adapter as the next priority.
2. External user feedback identifies a confirmed gap that cannot be resolved within the existing frozen baseline.
3. A project sponsor or lead author formally requests a new development phase via Notion control tower or GitHub.

No development activity resumes without a documented decision in the Notion control plane.

---

## Project Identity

**Name:** AI FANTUI LogicMVP
**Type:** Deterministic control-logic analysis workbench
**First Reference System:** Thrust reverser deploy cockpit
**Generalization Proof:** Landing-gear adapter runtime (second system)

## Core Truths

- `src/well_harness/controller.py` is the confirmed control truth.
- `src/well_harness/runner.py` is the simulation coordination layer.
- The simplified plant is a first-cut feedback model, not a complete physical model.
- New system truth is allowed only through explicit adapter interfaces.
- Bypassing adapters with new hardcoded truth paths is forbidden.

## Control Plane

- GitHub / repo is the code truth plane.
- Notion is the control plane and audit cockpit.
- GSD owns plan → execute → verify routing.
- Opus 4.6 is the only intended manual review gate for subjective judgment.

## Phase Registry

| Phase | Title | Status |
|-------|-------|--------|
| P0 | Control Tower And GSD Control Plane | Done |
| P1 | Automate Execution And Evidence Writeback | Done |
| P2 | Harden Opus 4.6 Review Packets | Done |
| P3 | Reduce Control-Plane Drift | Done |
| P4 | Elevate Cockpit Demo To Presenter-Ready | Done |
| P5 | Demo Polish And Edge-Case Hardening | Done |
| P6 | Reconcile Control Tower And Freeze Demo Packet | Done |
| P7 | Build A Spec-Driven Control Analysis Workbench | Done |
| P8 | Runtime Generalization Proof | Done |
| P9 | Automation Hardening & Evidence Pipeline Maturity | Done |
| P10 | Second-System Runtime Pipeline End-to-End | Done |
| P11 | Product Readiness & Third-Party Onboarding Guide | Done |
| P12 | Third-System Onboarding Validation | Done |
| P13 | Route B — Browser Workbench Multi-System Integration | Done |
| P14 | AI Document Analyzer | Done (2026-04-13) |
| P15 | Pipeline Integration — P14 output → P7/P8 intake | Done (2026-04-14) |
| P16 | AI Canvas Sync（Opus 4.6 架构裁决） | Done (2026-04-15) |
| P17 | Fault Injection — Interactive Fault Mode | Done (2026-04-15, self-signed v4.0; provenance re-signed 2026-04-20 P32) |
| P18 | Demo Cleanup & Archive Integrity | Done (2026-04-16, self-signed v4.0; provenance re-signed 2026-04-20 P32) |
| P19 | Hardware Partial Unfreeze — Monte Carlo + Reverse Diagnosis + Pitch Deck | Done (2026-04-17, self-signed v4.0; provenance re-signed 2026-04-20 P32; supersedes `docs/unfreeze/P17-application-draft.md`) |
| P20 | Wow E2E Coverage + Demo Resilience + Dress Rehearsal | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P32) |
| P21 | Local Model PoC — 国产模型本地降级 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P22 | Demo Rehearsal 物料冻结 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P23 | Co-development Kit — 立项通过后首批对接物料 | Done (2026-04-18, GATE-P23-CLOSURE Approved; 对外路线图编号 H2-23 ~ H2-27) |
| P24 | 立项后视觉硬化 — Canvas UI / AI Drawer / Demo Visuals | Done (2026-04-18, GATE-P24-CLOSURE Approved) |
| P25 | 立项汇报段落级时序彩排 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P26 | 立项物料引用有效性自动验证 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P27 | Backend Switch Drill — pkill+spawn+wait_ready | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P28 | FAQ Evidence Cross-Check | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P29 | Pre-Pitch Readiness Scorecard | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P30 | Scorecard 语义与 findings §5.1 决策对齐 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P31 | Explain-runtime visibility + prewarm guardrails (orphan-triage re-land) | Done (2026-04-20, v5.2 solo-signed; awaiting `P31-GATE: Approved` for FF merge to main) |
| P32 | Provenance Backfill — v4.0 追认 + Milestone 9 Lifted + constitution v2.1 | In progress (2026-04-20, v5.2 solo-signed; `GATE-P32-PLAN: Approved` 2026-04-20, awaiting `GATE-P32-CLOSURE: Approved`) |

---

## Milestone 9 — Project Freeze → Lifted

**Declared:** 2026-04-15 by Opus 4.6 Final Adjudication
**Lifted:** 2026-04-20 (retroactive provenance追认 under v5.2 Claude App Solo Mode, P32 W3)
**Scope:** Post-P16 freeze line covering all P17–P30 activity

### What Milestone 9 Meant

Opus 4.6 declared Project Freeze after P16 AI Canvas Sync (2026-04-15) with the assessment "项目已达到可泛化动力控制电路系统工作台 MVP 达标线". Freeze conditions required that continued development await one of three Resume Criteria: 外部用户反馈 / 产品方向决策 / 赞助方请求. `docs/freeze/FREEZE-RULING-2026-04-15.md` is the primary rulemaking document; `MILESTONE4/5/6-HOLD.md` are the earlier freeze-family records.

### Why It Was Lifted (retroactively 追认)

Between 2026-04-15 and 2026-04-18, under the v4.0 Extended Autonomy Mode then-in-force, **14 Phases (P17 → P30) landed above the freeze line**, each individually self-signed by the Executor (Codex / MiniMax-2.7 / Claude Code Opus 4.7) and accepted by Kogami through point-Gate decisions (`GATE-P23-CLOSURE: Approved`, `GATE-P24-CLOSURE: Approved`, etc.). These Gate approvals collectively satisfied Resume Criterion #1 「产品方向决策」 — Kogami's on-the-record directives to continue with 立项 demo hardening, co-development kit, then pitch script rehearsal constitute the required 产品方向 evidence.

**However**, the 14-Phase window **never carried an explicit Milestone 9 Lifted statement in this constitution**. That gap is what P32 W3 closes: not by retroactively re-consenting to work that already happened, but by正式 acknowledging that the freeze line was in fact crossed and the Resume Criterion path was met.

### Signatures

- **Kogami (Project Sponsor):** implicit Lifted consent via the 14 per-Phase Gate approvals (2026-04-15 → 2026-04-18); **explicit 追认 via `GATE-P32-PLAN: Approved` (2026-04-20)**
- **Claude App Opus 4.7 (Solo Executor, v5.2):** solo-signed 2026-04-20 via `.planning/phases/P32-provenance-backfill/P32-00-PLAN.md`

### What This Does NOT Mean

- Milestone 9 Lifted does **not** authorize new能力 Phases prospectively. Any new Phase (P33+) must still go through its own PLAN / CLOSURE Gate sequence under v5.2 Solo Mode.
- It does **not** imply `docs/freeze/FREEZE-RULING-2026-04-15.md` is void. That ruling stands as the 2026-04-15 factual assessment; Lifted simply记录 that the Resume Criteria were thereafter met.
- It does **not** alter any P17–P30 Phase content, tests, or code. P32 is证迹 (provenance) only.

---

## Governance Mode Timeline

- **v3.0 双 Opus (2026-04-xx → 2026-04-17):** Claude Code Opus 4.7 as Executor; Notion AI Opus 4.7 as independent Gate reviewer. Retired when v4.0 Extended Autonomy allowed Executor self-signing.
- **v4.0 Extended Autonomy (2026-04-17 → 2026-04-19):** Executor allowed to self-sign Gate within a ≥3-Phase深度验收 window when Kogami 显式 renewed the mandate. Used for P17 → P30 close-out.
- **v5.1 Pair Mode (2026-04-19 → 2026-04-20):** Short-lived dual-Executor pair (Claude App + Codex). Abandoned after orphan commit `4474505` (Codex, unsigned) triggered the P31 orphan-triage response.
- **v5.2 Claude App Solo Mode (2026-04-20, active):** Claude App Opus 4.7 as sole Executor. All Gate decisions (PLAN, CLOSURE) require explicit Kogami signature; Executor never self-selects the next Phase direction. See `v5.2 Solo Mode` section below for red lines.

## v5.2 Claude App Solo Mode (active)

### Red Lines (five absolutes)

1. **No controller.py / 19-node / R1–R5 / irreversible main-HEAD mutation without Kogami Gate sign.** FF merges, branch deletes, force-pushes, and any action that rewrites main's history must wait for an explicit `<PHASE>-GATE: Approved` comment from Kogami.
2. **No self-signed Gate.** Executor drafts `PLAN.md` and `CLOSURE.md` but never signs `GATE-<PHASE>-PLAN: Approved` or `GATE-<PHASE>-CLOSURE: Approved`. Those two signatures are Kogami-only.
3. **Tier 1 adversarial self-review is mandatory on every PLAN.** Plans must contain a Counterargument section with ≥3 reasoned self-objections and explicit rebuttals before request-for-Gate.
4. **Executor does not self-select next Phase direction.** When a Phase closes, Executor awaits Kogami's next directive. If Executor has a recommendation, it must be offered as an `AskUserQuestion` with ≥2 options, not acted on unilaterally.
5. **证迹 (provenance) precedes 能力 (capability).** New capability work is gated on no outstanding provenance debt. If gap analysis identifies provenance debt, that debt is closed in a dedicated证迹 Phase before any能力 Phase starts (this is precisely what P32 enforces for the v4.0 window).

### DECISION Format

Every Phase closure writes a DECISION section to the Notion control tower (`33cc68942bed8136b5c9f9ba5b4b44ec`) with heading:

```markdown
## Pxx DECISION · v5.2 solo-signed (YYYY-MM-DD)
```

Body covers: direction source · scope · Kogami Gate references · Exit artefact links · Red-line compliance checklist.

### Commit Trailer

Every commit by Claude App Opus 4.7 under v5.2 must include the trailer:

```
Execution-by: opus47-claudeapp-solo · v5.2
```

Reviewer sign line (in Notion / closure docs / audit records):

```
Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · YYYY-MM-DD
```

### Sandbox Discipline

- Workspace mount `.git/*.lock` residues are known blockers. v5.2 convention: scratch clone at `/sessions/<id>/p31-work/repo` + git bundle transfer when locks persist. Bundles live under `.planning/audit/bundles/` with adjacent README import instructions.
- Workspace mount file edits only permitted on paths that do NOT coincide with files changed by a pending bundle, to avoid FF merge conflicts.

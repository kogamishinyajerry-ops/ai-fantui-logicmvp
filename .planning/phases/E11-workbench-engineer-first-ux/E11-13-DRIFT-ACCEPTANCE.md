# E11-13 Drift Acceptance — P1 Tier-B R1 findings deferred to other E11 sub-phases

> Date: 2026-04-25
> Branch: `feat/e11-13-manual-feedback-trust-affordance-20260425`
> P1 R1 verdict: BLOCKER (2 BLOCKER + 4 IMPORTANT + 1 NIT)
> R1 verdict file: `.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md`

## In-scope fix (this PR)

| P1 finding | Severity | Action |
|---|---|---|
| #6 | IMPORTANT | **Fixed in R2 commit**. Banner copy now opens with scope definition: "What counts as 'manual feedback': any value you type to override an observed reading (e.g., editing a snapshot input before running a scenario, or marking an annotation as `override observed`). It does NOT include passive reads, replays, or audit-chain navigation." |

## Out-of-scope deferral (other E11 sub-phases own these)

| P1 finding | Severity | Why out of scope for E11-13 | Owning sub-phase |
|---|---|---|---|
| #1 | BLOCKER | Scenario Control panel ("Load Active Ticket" / "Snapshot Current State") affordance gap is the **column rename + role-action mapping** scope of E11-03 / E11-04. E11-13 spec (E11-00-PLAN §3 row E11-13) is explicitly trust-affordance UI only; not authority-action redesign. | **E11-03** (三列 verb 重命名 → "Probe & Trace / Annotate & Propose / Hand off & Track") + **E11-04** (annotation 词汇升级) |
| #2 | BLOCKER | Missing visible link from `/workbench` shell → `/workbench/bundle` runtime is by design per E11-09 split (PR #13) — the shell is meant to BE the collaboration surface, not a runtime launcher. The "junior can't find runtime entry" is the **onboarding-flow** scope of E11-02. | **E11-02** (`/workbench/start` 6-tile persona+role onboarding landing — already merged, but the *link from /workbench shell to /workbench/start or /workbench/bundle* needs an explicit affordance, scoped to **E11-04** column body or **E11-08** role-affordance signage) |
| #3 | IMPORTANT | "Annotation looks like drawing tools, not engineering notes" — annotation vocabulary upgrade is exactly **E11-04** scope. | **E11-04** |
| #4 | IMPORTANT | "Ticket value WB-E06-SHELL has no source/destination explanation" — this is the **column-body label semantics** scope of E11-03/E11-04. | **E11-03** + **E11-04** |
| #5 | IMPORTANT | "Identity 'Kogami / Engineer' + 'Kogami-only' Approval Center creates role confusion" — this is exactly the **role-affordance** scope of E11-08 ("非 Kogami 角色看到 Approval Center 时显示 'Pending Kogami sign-off' 而不是 disabled UI"). | **E11-08** |
| #7 | NIT | "Mixed `zh-CN` lang attribute + English UI labels" — this is the **i18n sweep** scope of E11-15. | **E11-15** |

## Why these are NOT new BLOCKERs introduced by E11-13

E11-13's diff is additive: 1 new chip + 1 new banner + 0 changes to existing affordances. Findings #1, #2, #3, #4, #5, #7 all describe pre-existing /workbench shell state observed by P1 with fresh eyes. The chip + banner did not regress any of these; they were already true on `main`.

P1's 30-minute onboarding test failure (gave up at ~12 min) is a **phase-level** signal that E11 is not yet closed, not a **sub-phase-level** rejection of E11-13. Per E11-00-PLAN §9 closure condition #3: "0 BLOCKER" applies to phase CLOSURE (E11-12), not to each individual sub-phase merge.

## Phase-level tracking

When E11-12 CLOSURE check runs, it must verify:
- E11-03 / E11-04 column rename addresses Finding #1, #2, #3, #4
- E11-08 role-affordance addresses Finding #5
- E11-15 i18n sweep addresses Finding #7
- The remaining BLOCKERs from any post-fix Codex re-review are 0 across all 5 personas (Tier-A) or the closing tier as fired

## Merge decision (E11-13 PR #16)

After R2 fix (Finding #6 addressed in commit), this PR merges with:
- 0 NEW BLOCKER from E11-13 alone
- 2 PRE-EXISTING BLOCKER (Findings #1, #2) deferred to owning sub-phases per spec
- 4 PRE-EXISTING IMPORTANT/NIT (Findings #3, #4, #5, #7) deferred to owning sub-phases per spec
- 1 E11-13-SPECIFIC IMPORTANT (Finding #6) FIXED in R2

This is consistent with the v6.1 Solo Autonomy delegation: phase scope discipline > sub-phase perfection. E11-12 is the closure gate for the BLOCKERs, not E11-13.

# E11-15b Surface Inventory — Chinese-first h2/button/caption sweep (iter 2)

> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
>
> Continuation of E11-15: that sweep covered 5 eyebrow labels; this iter
> covers the remaining English-only h1/h2/button/caption strings on
> /workbench, bilingualizing them as `<中文> · <English>` so the page is
> uniformly Chinese-first while preserving English suffixes for existing
> test locks.

## Surface diff inventory

| # | Surface | Type | Anchor | Notes |
|---|---|---|---|---|
| 1 | h1 `Control Logic Workbench` → `控制逻辑工作台 · Control Logic Workbench` | [REWRITE] | `workbench.html:18` | Page-level title above the brand eyebrow E11-15 already flipped. |
| 2 | btn `Load Active Ticket` → `加载当前工单 · Load Active Ticket` | [REWRITE] | `workbench.html:281` | First-column control panel skeleton button. |
| 3 | btn `Snapshot Current State` → `快照当前状态 · Snapshot Current State` | [REWRITE] | `workbench.html:282` | Second skeleton button in same column. |
| 4 | h2 `Review Queue` → `审核队列 · Review Queue` | [REWRITE] | `workbench.html:334` | Annotation-inbox aside heading. |
| 5 | btn text `Approval Center` → `审批中心 · Approval Center` | [REWRITE] | `workbench.html:349` | Bottom-bar approval entry button. The Kogami-only display copy is intentionally bilingualized; the API remediation message in `demo_server.py:743` is **NOT** touched (backend contract). |
| 6 | caption `Approval actions are Kogami-only.` → `审批操作仅限 Kogami · Approval actions are Kogami-only.` | [REWRITE] | `workbench.html:351` | Bottom-bar caption next to entry button. |
| 7 | h2 `Kogami Proposal Triage` → `Kogami 提案审批 · Kogami Proposal Triage` | [REWRITE] | `workbench.html:380` | Approval Center panel heading. |

## Out of scope (deliberately deferred or preserved)

- **Approval lane h3s** (`Pending`/`Accept`/`Reject`) + lane buttons
  (`Accept Proposal`/`Reject Proposal`) — functional approval-flow
  strings; deferred to a focused approval-flow polish sub-phase.
- **API remediation message** in `demo_server.py:743`
  (`"Acquire sign-off via Approval Center, or switch to auto_scrubber."`)
  — backend contract, locked by
  `tests/test_lever_snapshot_manual_override_guard.py:151`.
- **Column-trio eyebrows** + column h2s (already bilingual via E11-03).
- **Eyebrow labels** (already flipped by E11-15).
- **`workbench.js` / `workbench.css`** — pure HTML sweep.

## Tier-trigger evaluation

Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:

> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.

- **copy_diff_lines** = 7 → < 10
- **[REWRITE/DELETE] count** = 7 → ≥ 3

→ **Tier-B** (1-persona review). The first threshold (≥10) fails.

> **Verdict: Tier-B**. Persona = **P3 (Demo Presenter)** — round-robin
> successor of E11-15's P2 AND content-fit: this sub-phase is exactly
> typography / reading-rhythm / first-glance demo impression, which is
> P3's core lens.

## Behavior contract (locked by tests)

`tests/test_workbench_chinese_h2_button_sweep.py` (NEW, 28 tests):

1. Each of the 7 new bilingual strings is positively asserted.
2. 5 stale English-only patterns are asserted absent
   (button text fragments asserted via `>X<` to avoid false positives
   on the `Approval Center` substring inside `aria-controls` attributes).
3. 7 English-suffix invariants asserted preserved (so dual-route exact
   substring locks like `Control Logic Workbench</h1>` keep passing).
4. 7 structural anchors (IDs, class hooks, data-role attributes) asserted
   unchanged.
5. Live `/workbench` route serves all 7 new bilingual strings.
6. API remediation message in `demo_server.py` is asserted unchanged
   AND no Chinese strings leak into the backend file.

`tests/test_workbench_chinese_eyebrow_sweep.py` updated: line 119's
exact-string h1 lock changed from `<h1>Control Logic Workbench</h1>` to
`<h1>控制逻辑工作台 · Control Logic Workbench</h1>` to reflect the
bilingualization.

## Truth-engine red line

Files touched:
- `src/well_harness/static/workbench.html` — 7 strings flipped
- `tests/test_workbench_chinese_h2_button_sweep.py` — NEW (28 tests)
- `tests/test_workbench_chinese_eyebrow_sweep.py` — 1-line h1 lock update
- `.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended

Files NOT touched: `controller.py`, `runner.py`, `models.py`,
`src/well_harness/adapters/`, `workbench.js`, `workbench.css`,
`demo_server.py`. Truth-engine boundary preserved. No new endpoints; no
backend changes; the API remediation message is explicitly asserted
unchanged.

# E11-15 Surface Inventory — Chinese-first eyebrow sweep

> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.

## Scope rationale

Workbench has 8 eyebrow labels, all originally English-lowercase. 3 of them
(probe & trace / annotate & propose / hand off & track) are positively
locked by `tests/test_workbench_column_rename.py` and live above bilingual
h2 titles (`Probe & Trace · 探针与追踪`, etc.) — so the column trio already
provides Chinese-first signal at the h2 line and is intentionally
out-of-scope for this sweep.

The remaining 5 eyebrows live above either an English h1 (`Control Logic
Workbench`) or an English h2 (`Review Queue`, `Kogami Proposal Triage`)
or no h2 at all (state-of-world bar, canonical scenarios), and read
English-first at a glance. E11-15 flips them to pure Chinese so the page
reads Chinese-first across every section header. The h1/h2 strings
themselves are NOT touched (separate sub-phase if reformatting them is
desired).

## Surface diff inventory

| # | Surface | Type | Anchor | Notes |
|---|---|---|---|---|
| 1 | Page eyebrow `control logic workbench` → `控制逻辑工作台` | [REWRITE] | `workbench.html:17` | Top-of-page brand eyebrow above `<h1>Control Logic Workbench</h1>`. |
| 2 | State-of-world eyebrow `state of world` → `当前现状` | [REWRITE] | `workbench.html:62` | First label inside `#workbench-state-of-world-bar`. |
| 3 | Starters eyebrow `canonical scenarios` → `主流场景` | [REWRITE] | `workbench.html:97` | Above `<h2>起手卡 · One-click 走读</h2>`. |
| 4 | Annotation inbox eyebrow `annotation inbox` → `标注收件箱` | [REWRITE] | `workbench.html:333` | Above `<h2>Review Queue</h2>`. |
| 5 | Approval center eyebrow `approval center` → `审批中心` | [REWRITE] | `workbench.html:379` | Above `<h2 id="approval-center-title">Kogami Proposal Triage</h2>`. |

## Out of scope (preserved)

- **Column-trio eyebrows** (`probe & trace`, `annotate & propose`,
  `hand off & track`) — locked by E11-03 tests; bilingual h2 below
  already gives Chinese-first signal.
- **All h1/h2 strings** — reformatting from English-only to bilingual
  (e.g. `Review Queue` → `审核队列 · Review Queue`) is a separate
  sub-phase and would push this sweep to Tier-A.
- **`Approval Center` button text + Kogami-only caption** — functional
  approval-flow strings; deferred to a focused E11-XX sub-phase.
- **`workbench.js`, `workbench.css`** — pure HTML sweep; no
  selector/string drift.

## Tier-trigger evaluation

Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:

> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.

- **copy_diff_lines** = 5 → < 10
- **[REWRITE/DELETE] count** = 5 → ≥ 3

→ **Tier-B** (1-persona review). The first threshold (≥10) fails, so
even with all 5 lines being [REWRITE], the sub-phase stays Tier-B.

> **Verdict: Tier-B**. Persona = **P2 (Senior FCS Engineer)** — round-robin
> successor of E11-08's P1. P3 (Demo Presenter) would also fit content-wise
> (typography/reading-rhythm), but P3 has been used twice recently
> (E11-04, E11-05) so round-robin default applies. Senior FCS reviews
> visible-copy consistency + structural-anchor preservation, which is
> exactly the lens this sweep needs.

## Behavior contract (locked by tests)

`tests/test_workbench_chinese_eyebrow_sweep.py` (NEW, 22 tests):

1. Each of the 5 new Chinese eyebrow strings is positively asserted.
2. Each of the 5 stale English eyebrow strings is asserted absent.
3. The 3 E11-03 column eyebrows are asserted preserved.
4. h1, section IDs, and CSS class hooks (`eyebrow`, `workbench-sow-eyebrow`)
   are asserted unchanged.
5. Live-served `/workbench` route returns the new Chinese eyebrows.
6. The 5 new Chinese strings do NOT leak into `workbench.js` or
   `workbench.css` (HTML-only sweep).

## Truth-engine red line

Files touched:
- `src/well_harness/static/workbench.html` — 5 eyebrow strings flipped
- `tests/test_workbench_chinese_eyebrow_sweep.py` — NEW (22 tests)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended

Files NOT touched: `controller.py`, `runner.py`, `models.py`,
`src/well_harness/adapters/`, `workbench.js`, `workbench.css`. Truth-engine
boundary preserved. No new endpoints; no backend changes.

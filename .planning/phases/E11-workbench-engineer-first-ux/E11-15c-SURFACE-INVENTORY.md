# E11-15c Surface Inventory — column h2 direction flip + h1/eyebrow dedup

> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
>
> Direct closure of the 2 NITs raised by P3 Demo Presenter on E11-15b
> (`persona-P3-E11-15b-output.md:165-167`).

## NIT closure summary

| P3 NIT | Fix |
|---|---|
| #1: page eyebrow `控制逻辑工作台` immediately followed by h1 `控制逻辑工作台 · Control Logic Workbench` reads redundantly | Eyebrow flipped to `工程师工作区` so eyebrow + h1 read as category + title (two distinct semantic levels) |
| #2: column h2s are still English-first while the rest of the page is Chinese-first | 3 column h2s flipped from `<English> · <中文>` to `<中文> · <English>` for full-page direction consistency |

## Surface diff inventory

| # | Surface | Type | Anchor | Notes |
|---|---|---|---|---|
| 1 | Page eyebrow `控制逻辑工作台` → `工程师工作区` | [REWRITE] | `workbench.html:17` | Closes P3 NIT #1; eyebrow now reads as engineer-workspace sub-category, h1 stays as page title. |
| 2 | Column h2 `Probe & Trace · 探针与追踪` → `探针与追踪 · Probe & Trace` | [REWRITE] | `workbench.html:275` | Closes P3 NIT #2; English suffix preserved for substring locks. |
| 3 | Column h2 `Annotate & Propose · 标注与提案` → `标注与提案 · Annotate & Propose` | [REWRITE] | `workbench.html:295` | Same. |
| 4 | Column h2 `Hand off & Track · 移交与跟踪` → `移交与跟踪 · Hand off & Track` | [REWRITE] | `workbench.html:315` | Same. |

## Test contract updates (existing files touched in lockstep)

- `tests/test_workbench_column_rename.py`: 2 assertion blocks updated
  to expect Chinese-first column h2s (param values + live-route check).
- `tests/test_workbench_chinese_eyebrow_sweep.py`: page eyebrow lock
  updated from `控制逻辑工作台` to `工程师工作区`; truth-engine
  spot-check token list and live-route check updated to add
  `工程师工作区` while keeping `控制逻辑工作台` as a substring (still
  served via h1).
- `tests/test_workbench_chinese_direction_consistency.py` (NEW, 15 tests):
  positive locks for new strings, negative locks for stale, English suffix
  preservation, eyebrow-vs-h1 non-duplication invariant, live-served route,
  truth-engine isolation.

## Tier-trigger evaluation

Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:

> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.

- **copy_diff_lines** = 4 → < 10
- **[REWRITE/DELETE] count** = 4 → ≥ 3

→ **Tier-B** (1-persona review). The first threshold (≥10) fails.

> **Verdict: Tier-B**. Persona = **P4 (V&V Engineer)** — round-robin
> successor of E11-15b's P3 AND content-fit: this sub-phase rewrites
> existing test contracts in lockstep with HTML changes, so the V&V
> lens (verifying invariants are preserved across the contract migration)
> is exactly right.

## Behavior contract (locked by tests)

`tests/test_workbench_chinese_direction_consistency.py` (NEW, 15 tests):

1. 3 column h2s positively asserted Chinese-first.
2. 3 stale English-first column h2 strings asserted absent.
3. Page eyebrow positively asserted as `工程师工作区`; old `控制逻辑工作台` eyebrow asserted absent.
4. h1 still carries `<h1>控制逻辑工作台 · Control Logic Workbench</h1>` (E11-15b contract preserved).
5. Programmatic invariant: extracted eyebrow inner text != extracted h1 Chinese half — locks the dedup property.
6. 4 English suffixes preserved (`Probe & Trace</h2>`, etc.).
7. Live-served `/workbench` route serves all new strings.
8. Truth-engine isolation: new Chinese strings absent from `demo_server.py`/`controller.py`/`runner.py`/`models.py`/`workbench.js`/`workbench.css`.

## Truth-engine red line

Files touched:
- `src/well_harness/static/workbench.html` — 4 strings flipped
- `tests/test_workbench_column_rename.py` — 2 assertion blocks updated
- `tests/test_workbench_chinese_eyebrow_sweep.py` — eyebrow + truth-engine token list + live-route assertions updated
- `tests/test_workbench_chinese_direction_consistency.py` — NEW (15 tests)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended

Files NOT touched: `controller.py`, `runner.py`, `models.py`,
`src/well_harness/adapters/`, `workbench.js`, `workbench.css`,
`demo_server.py`. Truth-engine boundary preserved.

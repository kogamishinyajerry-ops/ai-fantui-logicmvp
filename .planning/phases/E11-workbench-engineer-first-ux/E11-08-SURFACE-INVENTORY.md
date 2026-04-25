# E11-08 Surface Inventory — role affordance for non-Kogami

> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.

## Surface diff inventory

| # | Surface | Type | Anchor | Notes |
|---|---|---|---|---|
| 1 | New attribute on identity chip: `data-identity-name="Kogami"` | [ANCHORED] | `#workbench-identity` | Source of truth for the role-affordance toggle. |
| 2 | New section icon `🛈` | [ANCHORED] | `#workbench-pending-signoff-affordance` (NEW) | Information glyph (distinct from the 🔒 authority banner). |
| 3 | Affordance headline `Pending Kogami sign-off` | [ANCHORED] | same section | Names the queued state directly. |
| 4 | Affordance body copy explaining the replacement of disabled UI | [ANCHORED] | same section | "你的提案已加入排队，等待 Kogami 处理。Approval 操作是 Kogami 专属 authority — 你的角色当前不会看到 disabled UI，而是这条 explicit '排队中' 提示。" |

## Tier-trigger evaluation

Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:

> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.

- **copy_diff_lines** = 4 → < 10
- **[REWRITE/DELETE] count** = 0 → < 3

→ **Tier-B** (1-persona review).

> **Verdict: Tier-B**. Persona = **P1 (Junior FCS Engineer)** — round-robin successor of E11-07's P5 AND content-fit: this is a small UI-only refactor with regression-risk concerns (CSS visibility toggle, JS attribute reading, URL-param parsing); P1 is the right lens.

## Behavior contract (locked by tests)

Default state (Kogami identity):
- `#approval-center-entry` visible (button)
- `#approval-center-panel` visible (full triage UI)
- `#workbench-pending-signoff-affordance` hidden (`data-pending-signoff="hidden"`)

Non-Kogami state (e.g., URL `?identity=Engineer`):
- `#approval-center-entry` hidden (with `aria-disabled="true"`)
- `#approval-center-panel` hidden
- `#workbench-pending-signoff-affordance` visible (`data-pending-signoff="visible"`)

Toggle path:
- `applyRoleAffordance()` reads `data-identity-name` from `#workbench-identity` and sets each target's visibility.
- `setWorkbenchIdentity(name)` exposed on `window` lets demo / tests flip identity programmatically.
- DOMContentLoaded honors `?identity=<name>` URL param so a demo can flip identity by URL alone.

## Truth-engine red line

Files touched:
- `src/well_harness/static/workbench.html` — added `data-identity-name="Kogami"` to identity chip; added new pending-signoff section
- `src/well_harness/static/workbench.css` — new `.workbench-pending-signoff*` selectors
- `src/well_harness/static/workbench.js` — new `applyRoleAffordance()` + `setWorkbenchIdentity()` functions; DOMContentLoaded `?identity=` parsing
- `tests/test_workbench_role_affordance.py` — NEW (10 tests)

Files NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. Truth-engine boundary preserved. No new endpoints; no backend changes. The identity attribute is a UI-only signal, not consumed by any backend route.

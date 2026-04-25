# E11-09 Surface Inventory (v2.3 §UI-COPY-PROBE)

> **Authored by:** Claude Code Opus 4.7 (1M context) · v6.1 Solo Autonomy
> **Date:** 2026-04-25
> **Sub-phase:** E11-09 dual-h1 fix (leading indicator per §3.6 of E11-00-PLAN)

## 0. Scope

This sub-phase splits `/workbench` (1078-line dual-h1 monolith) into two routes:
- `/workbench` → Epic-06..10 collab shell only (`workbench.html`, 171 lines, 1 h1)
- `/workbench/bundle` → legacy "Workbench Bundle 验收台" (new file `workbench_bundle.html`, 929 lines, 1 h1)

User-facing copy diff is small — only the page `<title>` of `/workbench` changes ("Well Harness Workbench Bundle 验收台" → "Control Logic Workbench") and 2 new HTML comments. The h1 texts themselves are unchanged at the source level; they just no longer co-exist in the same DOM.

## 1. Inventory table

| #  | Copy 出处 (file:line) | Claim 摘录 (≤40 字) | 类别 | Anchor / Plan-ID | 状态 |
|----|---|---|---|---|---|
| 1  | workbench.html:6 | `<title>Control Logic Workbench</title>` (was "Well Harness Workbench Bundle 验收台") | feature-name | src/well_harness/static/workbench.html:18 (matching h1 "Control Logic Workbench") | [ANCHORED] |
| 2  | workbench.html:165 | `<!-- E11-09 (2026-04-25): legacy "Workbench Bundle 验收台" content moved to /workbench/bundle. This page is now the Epic-06..10 shell only. -->` | surface-location | scope=src/well_harness/static/workbench.html (grep "Workbench Bundle 验收台</h1>" 0 hits); peer=src/well_harness/static/workbench_bundle.html:18 (h1 真实存在于新文件) | [ANCHORED] |
| 3  | workbench_bundle.html:6 | `<title>Well Harness Workbench Bundle 验收台</title>` | feature-name | src/well_harness/static/workbench_bundle.html:18 (matching h1 "Workbench Bundle 验收台") | [ANCHORED] |
| 4  | workbench_bundle.html:15 | `<!-- E11-09 (2026-04-25): legacy "Workbench Bundle 验收台" page, moved here from /workbench. The Epic-06..10 collab shell now lives on /workbench. -->` | surface-location | peer=src/well_harness/static/workbench.html:18 (Epic-06..10 shell h1 真实存在); scope=src/well_harness/static/workbench_bundle.html (grep "Control Logic Workbench</h1>" 0 hits) | [ANCHORED] |

## 2. Totals

- **ANCHORED:** 4
- **REWRITE-as-planned:** 0
- **DELETE:** 0

## 3. Commit trailer (per v2.3 §Trailer)

```
UI-Copy-Probe: 4 claims swept (4 anchored / 0 planned / 0 deleted)
```

## 4. Reviewer audit hooks (sample replays)

```bash
# Row #1 (title change on /workbench):
sed -n '6p' src/well_harness/static/workbench.html

# Row #2 (no Bundle h1 on shell page):
grep -c 'Workbench Bundle 验收台</h1>' src/well_harness/static/workbench.html  # → 0

# Row #3 (Bundle h1 only on bundle page):
grep -c 'Workbench Bundle 验收台</h1>' src/well_harness/static/workbench_bundle.html  # → 1

# Row #4 (no shell h1 on bundle page):
grep -c 'Control Logic Workbench</h1>' src/well_harness/static/workbench_bundle.html  # → 0
```

Each command's expected output is encoded in the inventory; reviewer can spot-check any 1-2 rows.

## 5. Notes

- E11-09 does **not** introduce new product copy. It is a pure surface relocation. Inventory is short by design (4 rows vs E11-02's 29 rows).
- New automated regression guard: `tests/test_workbench_dual_route.py` (7 tests) locks (a) `/workbench` has exactly 1 h1 + correct title + Epic-06..10 shell ids, (b) `/workbench/bundle` has exactly 1 h1 + correct title + bundle ids, (c) cross-file leakage prevented.
- Per §3.6 leading indicator gate: this PR's Codex round count determines whether v2.3 is amortized (≤2 rounds → 5-persona pipeline softens to tier-trigger via candidate `governance bundle #2`). Self-pass-rate estimate: **~80%** (small mechanical refactor, no new copy claims, comprehensive regression test).

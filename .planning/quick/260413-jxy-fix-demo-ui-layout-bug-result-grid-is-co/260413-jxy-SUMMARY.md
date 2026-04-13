# 260413-jxy-SUMMARY: Fix demo UI layout bug

**Quick Task:** 260413-jxy
**Objective:** Fix result-grid covered by sticky chain-panel when scrolling
**Date:** 2026-04-13
**Commit:** (pending)

## Changes Made

**File:** `src/well_harness/static/demo.css`

| # | Location | Change |
|---|----------|--------|
| 1 | Line ~324 (main grid-template-areas) | `"answer answer"` → `"result chain"` |
| 2 | Line ~331 (result-grid grid-area) | `grid-area: answer` → `grid-area: result` |
| 3 | Line ~2066 (≤1100px breakpoint) | `"answer"` → `"result"` |
| 4 | Line ~2196 (≤780px breakpoint) | `"answer"` → `"result"` |

## Verification

- `grep "answer" demo.css` → 0 matches (no remaining "answer" references)
- `grep "grid-area: answer" demo.css` → 0 matches
- `grep "result chain" demo.css` → line 324: `"result chain"` ✓
- `grep "grid-area: result" demo.css` → line 331: `grid-area: result` ✓

## Layout Behavior After Fix

- Main layout (≥1100px): `prompt | chain` (row 1), `result | chain` (row 2) — result and chain are side-by-side, chain-panel sticky behavior preserved
- Single-column (≤1100px): prompt → chain → result (vertical stack)
- No sticky chain-panel overlap since result is now in left column alongside chain

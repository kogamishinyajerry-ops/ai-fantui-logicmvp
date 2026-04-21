# P32 Provenance Backfill Git Bundle

**File:** `p32-provenance-backfill.bundle`
**Produced:** 2026-04-20 · v5.2 Claude App Solo Mode
**Contains:** 2 commits (atomic) —
  - `25f64fe` P31: re-land explain-runtime visibility + prewarm guardrails
  - `e6f9fe6` P32: provenance backfill — v4.0 window audit + Milestone 9 Lifted + constitution v2.1
**Base:** `dd915e1` (must be present in target repo)
**Branch produced:** `refs/heads/feat/p32-provenance-backfill`
**Author:** `Claude App Opus 4.7 <opus47-claudeapp-solo@local>` (both commits)
**Trailer:** `Execution-by: opus47-claudeapp-solo · v5.2` (both commits)

## Why this bundle (superset of P31)

The `p31-orphan-triage.bundle` file earlier in this directory contains only the P31 re-land commit. This newer `p32-provenance-backfill.bundle` **supersedes** it — it contains both P31 and P32 commits stacked linearly on `dd915e1`. Importing this one alone gets you both in one atomic FF merge.

## Gate requirements (both must be signed before FF merge)

1. **`P31-GATE: Approved`** — Kogami signature authorizing FF merge of `25f64fe` to main. Covers the P31 orphan-triage re-land (v5.2 first governance action).
2. **`GATE-P32-CLOSURE: Approved`** — Kogami signature authorizing FF merge of `e6f9fe6` to main. Covers the provenance backfill (W2-W6 done, W1 = the FF merge itself).

Either order is OK; W1 execution requires both.

## Import into your local clone (after both Gates signed)

```bash
# From the repo root:
git fetch "/path/to/p32-provenance-backfill.bundle" feat/p32-provenance-backfill:feat/p32-provenance-backfill

# Verify history looks right:
git log --oneline dd915e1..feat/p32-provenance-backfill
# Expected:
# e6f9fe6 P32: provenance backfill — v4.0 window audit + Milestone 9 Lifted + constitution v2.1
# 25f64fe P31: re-land explain-runtime visibility + prewarm guardrails (v5.2 solo triage of orphan 4474505)

# FF merge to main (both P31 + P32 atomic):
git checkout main
git merge --ff-only feat/p32-provenance-backfill

# Then clean up Codex残留:
git push origin --delete codex/p30-explain-runtime-sync
rm -rf .claude/worktrees/    # if any exist
```

If `git merge --ff-only` complains about untracked working tree files (likely
`.planning/phases/P32-provenance-backfill/P32-00-PLAN.md` which may have been
written directly to the mount earlier), run `rm -f` on the named file and retry
the merge — the bundle version will take over.

## Verify before accepting

```bash
git bundle verify p32-provenance-backfill.bundle
git log --format=fuller -2 feat/p32-provenance-backfill  # two commits, both with opus47-claudeapp-solo trailer
git diff --stat dd915e1 feat/p32-provenance-backfill
git show --format=full e6f9fe6 | head -60                # check P32 trailer
```

**Expected P32 commit diff stat:** `9 files changed, 573 insertions(+), 31 deletions(-)`
**Expected total diff stat (P31+P32):** ~30 files (P31) + 9 files (P32, with some overlap on `.planning/ROADMAP.md`) → approximately 32-33 unique files changed total

## Three-track test evidence (both pre-P32 and post-P32 identical)

- pytest default: **684 passed / 1 skipped / 49 deselected**
- opt-in e2e: **49 passed**
- adversarial: **8/8 PASS**

Delta between P31 baseline and P32 = zero (P32 changes governance/docs only, no src/ tests/ touched).

## Red-line compliance

Per v5.2 Claude App Solo Mode:
- ✅ controller.py / 19-node / R1-R5 / adapter discipline: all untouched
- ✅ Gate signatures pending Kogami (no Executor self-sign)
- ✅ Tier 1 adversarial self-review in `P32-00-PLAN.md §Counterargument Pre-check` (5 rebuttals)
- ✅ 证迹先行 principle: P32 itself is the first Phase enforcing this rule

## Related artefacts

- P32 plan: `.planning/phases/P32-provenance-backfill/P32-00-PLAN.md`
- P32 closure: `.planning/phases/P32-provenance-backfill/P32-05-CLOSURE.md`
- Earlier P31-only bundle: `p31-orphan-triage.bundle` (superseded by this file for any FF merge)
- P31 retroactive audit: `.planning/audit/P31-orphan-4474505-audit.md`
- Constitution v2.1 (Governance truth): `.planning/constitution.md` + `docs/architecture/constitution-v2.md`

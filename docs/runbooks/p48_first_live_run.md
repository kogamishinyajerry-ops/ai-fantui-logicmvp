# P48 first live run — revert PR #48 via the skill executor

**Status**: prerequisite for declaring the P48 弧 production-ready.
Run this once after P48-07 lands; success = the executor produces a
PR that, when merged, undoes PR #48's `tighten_condition` change.

**Why PR #48 specifically** (per Q8(c), 2026-04-27): a revert
proposal's "target ground truth" is the parent commit's file
contents, which is the cleanest correctness check for the
executor — if the resulting diff matches `git revert <sha>`, all
the safety machinery worked.

## Pre-flight

1. Verify pieces are wired:
   ```bash
   PYTHONPATH=src python3 -m pytest tests/ -q | tail -3
   # Expect: 1700+ passed
   ```
2. Verify MiniMax key resolves:
   ```bash
   PYTHONPATH=src python3 -c \
     "from well_harness.skill_executor import resolve_minimax_api_key as r; print(bool(r()))"
   # Expect: True
   ```
3. Confirm dev server is running on the same machine:
   ```bash
   make dev   # serves http://127.0.0.1:8780/workbench
   ```

## Step 1 — Backfill PR #48 audit

PR #48 landed before P48-05's gate. Without backfill, the gate
will block any subsequent revert PR (the revert PR's audit
references PR #48's landed SHA, but PR #48 has no audit so any
P47-02 revert flow looks orphaned).

```bash
PYTHONPATH=src python3 - <<'PY'
from well_harness.skill_executor import synthesize_backfill_audit
from pathlib import Path
record = synthesize_backfill_audit(
    proposal_id="PROP-20260426T075902988411-e27a6e",
    landed_sha="ec6f4fc94188fb3a7e68ef3763c3002b14ee105b",
    repo_root=Path("."),
    note="PR #48 dogfood; backfilled per Q7(a)",
)
print("backfilled:", record.exec_id)
PY
```

Commit the new audit:
```bash
git checkout -b chore/backfill-pr48-audit
git add .planning/skill_executions/EXEC-*-5ac669.json
git commit -m "chore: backfill audit for PR #48 dogfood (Q7(a))"
gh pr create --title "chore: backfill audit for PR #48" --body "Per Q7(a) (2026-04-27)..."
```

## Step 2 — Create the revert proposal

The workbench's "↩ 提议回退此修改" button (P47-02) creates a
revert proposal. From the inbox:

1. Open `http://127.0.0.1:8780/workbench`.
2. Find PR #48's proposal card (`PROP-20260426T075902988411-e27a6e`).
3. Click `↩ 提议回退此修改`. Confirm in the dialog.
4. The new revert proposal appears at the top of the inbox in
   OPEN state.
5. Note the new proposal id — call it `PROP-revert-XXX`.

Or via API directly:
```bash
curl -X POST http://127.0.0.1:8780/api/proposals/PROP-20260426T075902988411-e27a6e/propose-revert \
     -H 'Content-Type: application/json' -d '{"author_name":"Kogami"}'
```

## Step 3 — Accept the revert proposal

```bash
curl -X POST "http://127.0.0.1:8780/api/proposals/PROP-revert-XXX/accept" \
     -H 'Content-Type: application/json' -d '{"actor":"Kogami","note":"P48 first live run"}'
```

This writes `.planning/dev_queue/PROP-revert-XXX.md` (the brief
the executor reads).

## Step 4 — Run the executor

In a separate terminal:

```bash
RUN_LIVE_LLM=1 PYTHONPATH=src python3 -m well_harness.skill_executor \
    execute PROP-revert-XXX \
    --repo-root . \
    --approval-timeout-sec 1800
```

The CLI will print:

```
Executing proposal PROP-revert-XXX…
  ⏳ on ASKING state, will poll for workbench approval every 1.0s ...
```

It now blocks waiting for workbench approval.

## Step 5 — Approve the plan

Back in the browser, the proposal card now shows a cyan "Plan
待审" sub-card with:

- Plan rationale (from the LLM)
- Affected namespaces (should include `logic_truth`)
- File edits list (should reference `controller.py` /
  `models.py` / spec.json — undoing PR #48's additions)

If the plan looks correct, click `✅ 批准 · Approve`.

The CLI within ~1 second prints the rest of the pipeline:

```
EDITING → TESTING → PR_OPEN
  branch: revert/exec-PROP-revert-XXX-...
  pr:     https://github.com/.../pull/N
```

## Step 6 — Verify the PR

1. Open the new PR. Confirm:
   - Title is `revert(thrust-reverser): undo ec6f4fc per PROP-revert-XXX`
   - Branch is `revert/exec-PROP-revert-XXX-...`
   - Body ends with the EXEC-id stamp (`Exec-Id:` etc.)
   - Diff REMOVES PR #48's additions (`sw2_hysteresis_tra_deg`
     condition, the `logic2_sw2_max_tra_deg` field, the matching
     spec.json entry, and the corresponding test assertion line)
2. Confirm the **P48-05 audit gate** ran on the PR and passed
   (look for the `<!-- skill-executor-audit-gate -->` comment).
3. Confirm CI is green.

## Step 7 — Merge + record landed SHA

After the PR merges:

```bash
git checkout main && git pull
SHA=$(git log -1 --format=%H --grep="PROP-revert-XXX")
curl -X POST http://127.0.0.1:8780/api/proposals/PROP-revert-XXX/landed \
     -H 'Content-Type: application/json' \
     -d "{\"sha\": \"$SHA\", \"actor\": \"claude-code-executor\"}"
```

The audit JSON's state transitions PR_OPEN → LANDED.

## Step 8 — Verify the regression rolled back

```bash
PYTHONPATH=src python3 -m pytest tests/ -q | tail -3
# Expect: still 1700+ passed (the test suite was updated alongside
# the revert; nothing should fail)
grep -n "sw2_hysteresis_tra_deg" src/well_harness/*.py || \
    echo "✅ sw2_hysteresis_tra_deg fully removed from logic truth"
```

## Pass criteria

| Gate | Pass condition |
|---|---|
| Step 1 | Backfill audit committed + PR merged into main |
| Step 4 | CLI reaches ASKING state without errors |
| Step 5 | Approval card visible in workbench within 5s |
| Step 6 | PR title starts with `revert(`, body has stamp, diff is the inverse of PR #48 |
| Step 6 | P48-05 gate comments "Pass — audit chain validated" |
| Step 7 | `landed_truth_sha` recorded on the revert proposal |
| Step 8 | All tests still pass; `sw2_hysteresis_tra_deg` no longer appears in truth-engine code |

If ANY criterion fails, open a defect referencing the EXEC-id
+ the specific step, then patch the executor before retrying.
The runbook is meant to be reusable — patch + rerun.

## Cleanup

The dev-queue brief gets deleted automatically once Step 7
completes (the CLI's post-merge step removes it). Any
`.planning/proposals/PROP-*.json` files for test runs are
gitignored, so they accumulate locally — wipe periodically with:

```bash
rm -rf .planning/proposals/PROP-*-test* .planning/dev_queue/PROP-*-test*
```

The `.planning/skill_executions/` directory is **NOT**
gitignored (per Q3(b)) — every successful audit becomes a
permanent record.

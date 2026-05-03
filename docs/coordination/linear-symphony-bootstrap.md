# Linear/Symphony Bootstrap

Status: active bootstrap · created 2026-05-03

## Control Model

- Linear is the work/control surface for issue intent, queue state, and proof comments.
- Codex is the primary implementation executor.
- GitHub and the repo are the code truth, PR truth, and validation evidence surface.
- OpenAI Symphony is the bounded queue/gate model: discover an eligible Linear issue, execute one scoped repo run, publish proof, and stop at explicit review or merge gates.
- Notion remains record/control-plane sync only. It does not override repo or GitHub evidence.

## Live Linear Mapping

Live Linear issue:

- `JER-229`: `AI FANTUI LogicMVP · v6 next-queue bootstrap`
- URL: `https://linear.app/jerrykogami/issue/JER-229/ai-fantui-logicmvp-v6-next-queue-bootstrap`
- Proof comment: `https://linear.app/jerrykogami/issue/JER-229/ai-fantui-logicmvp-v6-next-queue-bootstrap#comment-09cd9a49`
- `JER-230`: `[project] [L9] [none] [DAL-TBD] Post-v5 v6 live queue seed`
- URL: `https://linear.app/jerrykogami/issue/JER-230/project-l9-none-dal-tbd-post-v5-v6-live-queue-seed`
- Project: `AI FANTUI LogicMVP · Codex Daily Lane`

Important mapping rule:

- Live Linear `JER-229` is not the same artifact as the repo-local historical `JER-229` Workbench v5 launch slice.
- Live Linear `JER-230` is not the same artifact as the repo-local historical `JER-230` empty-canvas graph authoring slice.
- When an identifier collides, write both surfaces explicitly: `live Linear JER-229` versus `repo-local JER-229`.
- Future Symphony/Codex work should prefer the live Linear issue identity when dispatching, then cite repo-local sequence labels only as implementation history.

## Current Evidence

- PR #216 merged JER-234 sandbox runner trace kernel: `4b68cf8`.
- PR #217 merged JER-235 debug probe timeline: `771a69a`.
- PR #218 merged JER-236 hardware evidence attachments: `ab2ad2f`.
- PR #219 merged JER-237 editor command palette: `02a0bee`.
- PR #220 merged JER-238 review archive restore bundle: `6c8c404`.
- PR #221 merged validation-suite timeout maintenance: `37195fc`.
- `uv run --locked python tools/run_gsd_validation_suite.py` passed 25/25 on post-v5 `main` after #221.

## Known Gaps

- Live Linear issues for repo-local JER-234 through JER-238 do not exist in the current Linear API. Direct proof comment dry-runs against those issue keys returned `Entity not found: Issue`.
- The newly created live Linear `JER-229` issue is a bootstrap/control-plane issue. It should not be used to imply that the repo-local v5 launch slice was reopened.
- Live Linear `JER-230` is the first post-v5 implementation queue seed. Its repo-side execution record is `docs/coordination/post-v5-v6-live-queue.md`.
- No Linear state transition was performed; only one proof comment was written.

## Next Work Policy

1. Discover live Linear issues first with `linear_awcp.py discover --team-key JER`.
2. Execute only one eligible issue per Codex run unless the user explicitly authorizes broader orchestration.
3. Keep controller truth, frozen adapters, certified hardware YAML, and C919 reference packets read-only unless a separate truth-gate issue explicitly permits changes.
4. For post-v5 work, create or select a live Linear issue with Outcome, Acceptance, Boundaries, Evidence Required, Repository, Desired state, and Agent eligible metadata before implementation.
5. Publish concise proof comments only after dry-run review; never paste secrets, raw logs, or state transitions into Linear by default.

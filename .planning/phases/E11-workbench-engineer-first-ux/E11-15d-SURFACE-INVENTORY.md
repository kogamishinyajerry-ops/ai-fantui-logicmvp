# E11-15d Surface Inventory — approval-flow polish

> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
>
> Bilingualizes the Approval Center lane labels + buttons + pending-lane
> body copy (6 strings). Note: this is NOT the final Chinese-first
> sweep — see "English-only surfaces still remaining" below for what
> stays English after this sub-phase. P2 R1 review IMPORTANT closure:
> earlier draft of this inventory overclaimed "last English-only surface"
> and "uniformly Chinese-first" — corrected.

## Surface diff inventory

| # | Surface | Type | Anchor | Notes |
|---|---|---|---|---|
| 1 | h3 `Pending` → `待审 · Pending` | [REWRITE] | `workbench.html:384` | Approval Center pending-lane heading. |
| 2 | Pending body `Submitted annotation proposals wait here before acceptance or rejection.` → bilingual `已提交的标注提案在被通过或驳回前在此排队 · ...` | [REWRITE] | `workbench.html:385` | Pending-lane explanatory copy. |
| 3 | h3 `Accept` → `通过 · Accept` | [REWRITE] | `workbench.html:388` | Accept-lane heading. |
| 4 | btn `Accept Proposal` → `通过提案 · Accept Proposal` | [REWRITE] | `workbench.html:389` | Accept-lane action button. |
| 5 | h3 `Reject` → `驳回 · Reject` | [REWRITE] | `workbench.html:392` | Reject-lane heading. |
| 6 | btn `Reject Proposal` → `驳回提案 · Reject Proposal` | [REWRITE] | `workbench.html:393` | Reject-lane action button. |

## Out of scope (deliberately preserved)

- **API remediation message** in `demo_server.py:743` — backend
  contract, locked by
  `tests/test_lever_snapshot_manual_override_guard.py:151`.
- **Approval Center entry button + Kogami-only caption** — already
  bilingualized by E11-15b PR #25.
- **`approval-center-title` h2** — already bilingualized by E11-15b
  PR #25.
- **`workbench.js` / `workbench.css`** — pure HTML sweep.
- **`data-approval-action`/`data-approval-lane` attributes** — preserved
  as structural anchors for any JS bindings or e2e selectors.

## Tier-trigger evaluation

Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:

> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.

- **copy_diff_lines** = 6 → < 10
- **[REWRITE/DELETE] count** = 6 → ≥ 3

→ **Tier-B** (1-persona review).

> **Verdict: Tier-B**. Persona = **P2 (Senior FCS Engineer)** —
> derived programmatically by
> `python3 tools/codex_persona_dispatch.py next-persona` (returned `P2`
> as the round-robin successor of E11-10's P1). First sub-phase to use
> the E11-10 tooling for persona selection.

## Behavior contract (locked by tests)

`tests/test_workbench_approval_flow_polish.py` (NEW, 25 tests):

1. 6 new bilingual strings positively asserted.
2. 5 stale English-only patterns asserted absent.
3. 6 English suffixes preserved (`Pending</h3>`, `Accept Proposal</button>`, etc.).
4. 6 structural anchors (data-approval-lane / data-approval-action /
   workbench-approval-grid class) asserted unchanged.
5. Live-served `/workbench` route serves all 6 new bilingual strings.
6. Backend isolation: `demo_server.py` remediation message unchanged
   AND no Chinese leak into the backend file.

## Truth-engine red line

Files touched:
- `src/well_harness/static/workbench.html` — 6 strings flipped
- `tests/test_workbench_approval_flow_polish.py` — NEW (25 tests)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended (via tool)

Files NOT touched: `controller.py`, `runner.py`, `models.py`,
`src/well_harness/adapters/`, `workbench.js`, `workbench.css`,
`demo_server.py`. Truth-engine boundary preserved.

## Workbench Chinese-first thread progress (NOT closure)

E11-15d is one slice in a multi-sub-phase Chinese-first thread:
- E11-15: 5 eyebrows
- E11-15b: h1 + 2 buttons + h2 + entry button + caption + h2
- E11-15c: 3 column h2s + page eyebrow dedup
- **E11-15d: 3 lane h3s + 2 lane buttons + 1 body copy** (this sub-phase)

## English-only surfaces still remaining (NOT in this sub-phase)

P2 R1 review identified these surfaces still English-only on /workbench
after E11-15d. They are deferred to follow-up sub-phases:

- `Hide for session` (workbench.html:225) — trust banner dismiss button.
  Locked by `tests/test_workbench_trust_affordance.py:66,135`.
- `Truth Engine — Read Only` (workbench.html:248) — authority banner
  headline. Locked by `tests/test_workbench_authority_banner.py:75,131`.
- `No proposals submitted yet.` (workbench.html:337) — annotation inbox
  empty-state placeholder.
- `Pending Kogami sign-off` (workbench.html:363) — affordance strong
  text. Locked by `tests/test_workbench_role_affordance.py:73`.
- WOW starter card h3s (workbench.html:111, 143, 173) — `Causal Chain ·
  因果链走读` etc. are English-first; same direction-flip pattern as
  E11-15c column h2s could apply.
- Topbar chip labels (`Identity` / `Ticket` / `Feedback Mode` / `System`)
  — left as functional labels next to dynamic content.

The backend API remediation message in `demo_server.py:743` is also
intentionally preserved as backend contract.

A future E11-15e sub-phase can cover the trust-banner / authority-headline
/ inbox-placeholder / affordance-strong / WOW-h3-direction strings as
a Tier-A bundle (estimated 7+ REWRITE → Tier-A).

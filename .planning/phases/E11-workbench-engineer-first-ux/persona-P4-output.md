PERSONA: P4 (ZHANG Mei, V&V engineer, audit-focused)
VERDICT: BLOCKER

## Audit-chain integrity 1-line summary
Partial only: I can reconstruct `SR-04/FR-04 -> logic4 -> controller -> unit/API tests` offline, but I cannot complete a certifiable requirement -> design -> code -> test -> immutable review-record chain through the Workbench; this would not pass a DO-178C trace audit.

Representative invariant probed: requirement basis in `docs/thrust_reverser/requirements_supplement.md:96-125` and `src/well_harness/static/fantui_requirements.html:215-238`, design node in `src/well_harness/system_spec.py:490-500`, code in `src/well_harness/controller.py:107-159`, tests in `tests/test_controller.py:174-180` and `tests/test_demo.py:490-600`. The review-record leg is where the chain breaks.

## Findings (5-10, numbered, severity BLOCKER|IMPORTANT|NIT)

1. [BLOCKER] Spec Review Surface — actual requirement evidence is missing from the audited Workbench surface.
   Audit-chain element at risk: requirement
   Airworthiness blast-radius: cannot-certify
   Evidence: `src/well_harness/static/workbench.html:72-88` shows placeholder copy only; `src/well_harness/static/workbench.js:71-75` explicitly says text-range annotation is future work.
   Suggested mitigation (audit-language, not UI redesign): load controlled source requirements with requirement IDs, revision, authority, and source SHA-256; placeholder prose is not auditable evidence.

2. [BLOCKER] Requirement authority for `deploy_90_percent_vdt >= 90%` is reverse-backfilled, not cleanly carried from an upstream requirement.
   Audit-chain element at risk: requirement
   Airworthiness blast-radius: cannot-certify
   Evidence: the supplement states the original docx mentioned "fully deployed" but did not contain the percentage threshold, then backfills `90.0%` from code (`docs/thrust_reverser/requirements_supplement.md:96-125`). Registry authority remains internal self-sign, not external approval (`docs/provenance/adapter_truth_levels.md:44-46`).
   Suggested mitigation (audit-language, not UI redesign): disposition this as a controlled derived requirement with stable ID, authority basis, and approval record; do not present code-to-spec backfill as if it were a normal upstream requirement flow.

3. [IMPORTANT] Logic Circuit Surface does not let an auditor navigate from a gate to its requirement/design/test evidence.
   Audit-chain element at risk: design, test
   Airworthiness blast-radius: cannot-certify
   Evidence: `src/well_harness/static/workbench.html:91-112` is a six-label circuit skeleton with no gate trace payload. The real linkage exists only in separate artifacts: `src/well_harness/static/fantui_requirements.html:340-362` and `src/well_harness/system_spec.py:490-500`.
   Suggested mitigation (audit-language, not UI redesign): for each gate, expose a frozen trace tuple: requirement IDs, design-node ID, code anchor, validating test IDs, and last approved review record ID.

4. [IMPORTANT] Annotation Inbox is freeform local draft storage, not trace-controlled review evidence.
   Audit-chain element at risk: review record
   Airworthiness blast-radius: medium
   Evidence: annotation drafts persist in browser `localStorage` and carry only `tool/surface/note/author/ticket/system` plus an anchor (`src/well_harness/static/annotation_overlay.js:68-100`, `117-128`). The proposal schema requires no `requirement_id`, `test_id`, `artifact_hash`, or review linkage (`src/well_harness/workbench/proposals.py:52-64`, `74-104`).
   Suggested mitigation (audit-language, not UI redesign): require every review annotation to reference controlled artifact IDs and affected requirement/test IDs before it enters any approval queue.

5. [BLOCKER] Approval Center is present as a UI shell, but not as a connected, auditable workflow.
   Audit-chain element at risk: review record
   Airworthiness blast-radius: cannot-certify
   Evidence: the UI exposes triage lanes and buttons (`src/well_harness/static/workbench.html:126-160`), but `demo_server.py` only exposes `/api/workbench/bootstrap|bundle|repair|archive-restore|recent-archives` (`src/well_harness/demo_server.py:70-74`, `1132-1146`). The associated test only checks static lane presence (`tests/test_workbench_approval_center.py:84-90`).
   Suggested mitigation (audit-language, not UI redesign): treat approval as a controlled review transaction tied to immutable artifacts and persisted review objects, not as a presentational affordance.

6. [BLOCKER] The hash-chained audit model does not hash the reviewed artifact set.
   Audit-chain element at risk: review record
   Airworthiness blast-radius: cannot-certify
   Evidence: `AuditEventLog` correctly chains `previous_hash` and `event_hash` (`src/well_harness/workbench/audit.py:43-67`), and `ApprovalCenter` uses server-side stamping in the current approval path (`src/well_harness/workbench/approval.py:30-41`, `54-67`). But the signed payload only contains `path/tool/surface` or `reason/ticket/system`; it does not contain the reviewed requirement revision, code hash, test result hash, or bundle manifest hash. The committed `audit/events.jsonl:1-2` sample is not hash-chained at all.
   Suggested mitigation (audit-language, not UI redesign): sign the reviewed artifact references themselves inside the event envelope and require a manifest/hash set for approval closure.

7. [IMPORTANT] The nearest available "review record" for the invariant is archived QA prose, not a controlled approval object.
   Audit-chain element at risk: review record
   Airworthiness blast-radius: medium
   Evidence: `docs/coordination/archive/qa-report-history.md:198-216` records a live check that `logic4 / THR_LOCK` is blocked on `deploy_90_percent_vdt`, but it is prose history only: no immutable artifact set, no requirement ID binding, and no review record identifier that closes the chain.
   Suggested mitigation (audit-language, not UI redesign): promote such observations into controlled review records with reviewer identity, timestamp, artifact set, verdict, and closure status.

## Hash-chained audit log probe

- `prev_hash actually chains`: Pass for code-generated events. `src/well_harness/workbench/audit.py:59-63` creates the chain, and a temp probe with `proposal.submitted -> proposal.accepted` produced `previous_hash == prior event_hash`. Fail for the committed repository sample: `audit/events.jsonl:1-2` contains schema-registration rows only, without live chain fields.
- `entry timestamp is an authoritative source`: Conditional pass. In the current `ApprovalCenter` flow, timestamps are server-generated through `_utc_now()` and `AuditEventLog.append()` (`src/well_harness/workbench/approval.py:30-41`, `54-67`; `src/well_harness/workbench/audit.py:16-17`, `59`). But `append(..., observed_at=...)` allows caller override, so the authority boundary is not absolute.
- `hash covers an immutable artifact reference`: Fail. The signed payload omits reviewed-artifact SHA-256 / manifest hash and therefore does not prove what was reviewed. For certification context, this is a BLOCKER.

## Anti-bias check

P1/P2/P3/P5 would likely stop at "the surface is placeholder" or "the buttons are not wired." The V&V-specific finding is stricter: even if those surfaces were visually complete tomorrow, this still fails an airworthiness-style audit because the approval event is not cryptographically bound to the exact requirement revision, design snapshot, code artifact, test evidence set, and reviewer disposition. That is not a presentation defect; it is a broken certification audit chain.

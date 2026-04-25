PERSONA: P2 (CHEN Wei, Senior FCS, 10y reverser exp)
VERDICT: BLOCKER

## Authority-contract assessment (1 paragraph)
As presented, this Workbench does not yet enforce a clean who-can-write-what boundary. It says `controller.py` is the truth source, but the demo surface lets an operator drive `deploy_position_percent` directly (`src/well_harness/static/demo.html:96-100`, `src/well_harness/static/demo.js:107-119`), and that path can produce `logic4_active=true` / `THR_LOCK release` with L3 false at `RA=6.0` through `/api/lever-snapshot`. On the Workbench side, “冻结审批 Spec” is a browser-side freeze action gated only by UI state, not by a server-enforced role/ticket path (`src/well_harness/static/workbench.js:121-131`, `443-470`). So I can inspect behavior, but I would not treat this as a controlled engineering review surface yet; if you ask me to assess a change like `reverse_travel_max_deg: -8 -> -5`, I still have to leave the UI and read code/API truth.

## Findings (5-10, numbered, severity BLOCKER|IMPORTANT|NIT)

1. [BLOCKER] `src/well_harness/controller.py:107-135`, `src/well_harness/demo_server.py:1799-1843`, surface probe `/api/lever-snapshot {tra_deg:-14, radio_altitude_ft:6.0, deploy_position_percent:100, feedback_mode:"manual_feedback_override"}` — L4 / THR_LOCK can assert while L3 is false.
   Authority/spec link at risk: deploy authority chain, upstream interlock precedence, release command must not outrun authorized deploy path.
   Suggested mitigation: make L4 depend on an authorized deploy lineage, not a standalone feedback surrogate; I would want the reverser release-path requirement and its verification case tied here explicitly.

2. [BLOCKER] `src/well_harness/static/workbench.html:546-547`, `src/well_harness/static/workbench.js:121-131`, `443-470`, `3649-3656`, contrasted with `src/well_harness/workbench/approval.py:20-22,54-68` — the visible “冻结审批 Spec” path is client-side only and bypasses the server-side Kogami authority check that exists elsewhere in the repo.
   Authority/spec link at risk: approval boundary and audit authority; a browser user can appear to freeze an engineering spec without controlled backend authorization.
   Suggested mitigation: route freeze/approve through a single server API with actor identity, proposal ID, ticket ID, and immutable audit event hash.

3. [IMPORTANT] `src/well_harness/static/demo.html:571-574` versus `src/well_harness/controller.py:107-135` — the review surface says `L4 = L3 AND VDT >= 90%`, but the truth code evaluates `VDT90 + TRA range + ground + engine`, with no direct L3 condition.
   Authority/spec link at risk: traceability and review correctness; the engineer is not being shown the real gate definition.
   Suggested mitigation: render the exact `DeployController.explain(logic4)` condition set, including comparison and threshold values, not a simplified paraphrase.

4. [IMPORTANT] `src/well_harness/demo_server.py:1633-1703` — the narrative summary can contradict the truth table. At `TRA=-4` with VDT forced high, outputs show `logic4_active=true`, yet summary still says the chain is blocked at SW2.
   Authority/spec link at risk: deterministic review evidence; narrative text must never outrank the evaluated truth state.
   Suggested mitigation: generate summary text from evaluated outputs / failed conditions only, with no pre-ordered story branch that can mask an asserted downstream command.

5. [IMPORTANT] `src/well_harness/models.py:92-108`, `src/well_harness/static/demo.html:125-215` — there is no LOSS/NCD/FROZEN-VALUE input-quality model, only raw values plus ad hoc fault injection.
   Authority/spec link at risk: degraded-mode response definition. A reverser review needs declared behavior for invalid, stale, disagreeing, or substituted inputs.
   Suggested mitigation: add validity/status to the input contract and show gate response for degraded input classes, not only `sensor_zero` / `stuck_false`.

6. [IMPORTANT] `src/well_harness/system_spec.py:29-45`, `448-501`, surface area `workbench onboarding/fingerprint/actions` — logic notes exist, but there is no requirement ID / clause / test-case linkage per gate.
   Authority/spec link at risk: clause-level traceability. I can read the logic, but I cannot answer “which requirement section governs this gate?” from the Workbench.
   Suggested mitigation: add requirement references and verification IDs at condition/node level, then display them where the reviewer inspects each gate.

7. [IMPORTANT] `src/well_harness/controller_adapter.py:101-109`, `src/well_harness/workbench_bundle.py:921-957`, `src/well_harness/static/workbench.js:3069-3089` — truth metadata and SHA256 integrity exist in code/archive, but the UI does not make the truth-engine version/hash immutably visible.
   Authority/spec link at risk: audit chain. A reviewer can see file paths, not the exact truth artifact identity being signed against.
   Suggested mitigation: pin adapter ID, metadata version, source-of-truth path, and archive manifest hash in the visible review header.

8. [IMPORTANT] `src/well_harness/demo_server.py:1600-1616`, `src/well_harness/static/workbench.js:1937-1968` — if the customer asks to change `reverse_travel_max_deg` from `-8` to `-5`, the UI does not show an impact set. The API exposes thresholds, but history compare only shows counts, not changed thresholds or affected cases.
   Authority/spec link at risk: change-impact review. By code I can infer the valid L4 travel window shrinks; the Workbench does not show which scenarios/tests flip.
   Suggested mitigation: add threshold diffs, impacted gate list, and linked regression cases to the change-review path.

## Truth-engine red-line check

Yes — the VDT slider explicitly tells the user it can directly drive `VDT90 -> L4 -> THR_LOCK` (`src/well_harness/static/demo.html:96-100`), and current behavior shows that appearance is not merely cosmetic.

## Anti-bias check

P1/P3/P4/P5 may complain about clarity or demo fidelity, but the senior-domain finding they are most likely to miss is Finding 1: `L4` releasing with `L3=false` at `RA=6.0`. That is not a presentation defect; it is an authority-chain breach. A reverser engineer reads that as “release path escaped its upstream authorization,” which is precisely the kind of issue that blocks signoff even when the screen still looks plausible.

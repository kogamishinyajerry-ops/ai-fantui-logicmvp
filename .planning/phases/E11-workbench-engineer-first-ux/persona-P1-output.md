PERSONA: P1 (WANG Lei, Junior FCS, 3-month hire)
VERDICT: APPROVE_WITH_COMMENTS

## 1-sentence onboarding assessment
Yes I could do this without help: after I ignored the top `Ticket / Annotation / Kogami` area and used the lower `一键通过验收` or `载入参考样例 -> 生成 Bundle` path, I could understand how to run the reverse-thrust reference path.

## Findings (5-10, numbered, each with severity BLOCKER|IMPORTANT|NIT)

1. [IMPORTANT] `src/well_harness/static/workbench.html:15-37,165-185` — The first screen shows `Control Logic Workbench`, `Kogami / Engineer`, `Ticket`, and `System`, but the real task entry is lower down in `Workbench Bundle 验收台`, so my first reaction was “am I in a collaboration console instead of the run page?” Why this matters for a junior: first-screen framing decides whether I act or hesitate. Suggested fix: make the run path the dominant first object and demote the governance chrome.

2. [IMPORTANT] `src/well_harness/static/workbench.html:50-68,188-245`; `src/well_harness/static/workbench.js:63-82` — `Scenario Control` looks like the place to run a scenario, but its buttons feel like shell affordances while the real action is lower in the preset cards or `载入参考样例 + 生成 Bundle`; the status text even says scenario actions are staged for `E07+`. Why this matters for a junior: I will click the wrong button first because it is higher and looks more official. Suggested fix: either hide that shell in junior view or label it clearly as non-running prototype UI.

3. [IMPORTANT] `src/well_harness/static/workbench.html:39-47,116-123`; `src/well_harness/static/annotation_overlay.js:68-100,117-128` — `Annotation` is not explained in operator language: I can infer it drops point/area/link/text markers onto the three top panels, and the result appears in `Review Queue`, but there is no obvious note box or sentence saying whether this is my working note, a proposal, or a shared review artifact. Why this matters for a junior: unclear note behavior makes me avoid touching it. Suggested fix: add one plain sentence saying what annotation is for and where it goes.

4. [IMPORTANT] `src/well_harness/static/workbench.html:24-27,66-67,318-320` — `Ticket` shows `WB-E06-SHELL`, and there is a `Load Active Ticket` button, but the page never explains where the ticket comes from, whether I need to choose one, or whether running the scenario depends on it. Why this matters for a junior: ticket IDs look like prerequisites, so I worry I am skipping a required step. Suggested fix: explain the ticket lifecycle in one line or hide it from the acceptance flow.

5. [IMPORTANT] `src/well_harness/static/workbench.html:126-160` — `Kogami Proposal Triage` is visibly on the same page, but the footer also says approval actions are Kogami-only, so as a junior I read it as “this is someone else’s lane, not mine,” yet it still competes for attention with my run task. Why this matters for a junior: role-inaccessible UI creates authorization anxiety. Suggested fix: collapse it behind a reviewer-only drawer or explicitly mark it as out-of-scope for engineers just running scenarios.

6. [NIT] `src/well_harness/static/workbench.html:6,17-18,39-44,168-185,545-549,997-1030` — The page mixes several names and languages at once: `Control Logic Workbench`, `Workbench Bundle 验收台`, `返回反推逻辑演示舱`, plus English blocks like `Playback Snapshot` and `Knowledge Artifact`; I can still operate it, but it feels like internal language leaked into the operator surface. Why this matters for a junior: mixed naming makes me unsure which terms are real workflow concepts and which are dev leftovers. Suggested fix: pick one primary page name and one operator vocabulary baseline.

## Anti-bias check — at least one finding I'd expect OTHER personas to MISS

Finding 4. Someone already familiar with the project will instantly dismiss `WB-E06-SHELL` as context chrome, but P1 sees `Ticket` plus `Load Active Ticket` and assumes there may be a missing prerequisite before any reverse-thrust run; that hesitation is very specific to a new-hire view.



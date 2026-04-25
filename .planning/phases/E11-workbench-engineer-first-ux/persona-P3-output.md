PERSONA: P3 (LIU Yifei, Demo Presenter, 7 days to pitch)
VERDICT: BLOCKER

## Stage-readiness 1-line summary
No; if I'm in front of the panel right now, `/workbench` feels like an engineer acceptance page, not a 3-wow pitch surface, and wow_b / wow_c are not discoverable fast enough.

## Findings (5-10 numbered, severity BLOCKER|IMPORTANT|NIT)

1. [BLOCKER] `/workbench` first screen is the wrong room
   Stage scenario where this hurts: if I say "先看 wow_a", the panel first sees `Identity / Ticket / Annotation / Approval Center`, and I look like I opened an internal tool.
   Suggested mitigation (presentation-friendly): default to a clean presenter landing with only 3 wow cards + reset; hide collaboration chrome behind `工程模式`.

2. [BLOCKER] wow_b / wow_c are not discoverable
   Stage scenario where this hurts: when I need `Monte Carlo` or `反向诊断`, I cannot find a button with that name on `/workbench` or `/demo.html`, so I burn stage time hunting nav.
   Suggested mitigation (presentation-friendly): add one-click buttons `wow_a 因果链 / wow_b Monte Carlo / wow_c 反向诊断`, each with a fixed opening state.

3. [BLOCKER] no visible narration fallback
   Stage scenario where this hurts: if AI narration is slow or down, I still need one sentence I can read immediately, but I do not see a stable on-screen `headline / blocker / next step` card.
   Suggested mitigation (presentation-friendly): always render a local fallback narration ribbon from deterministic response fields.

4. [IMPORTANT] mixed-language UI
   Stage scenario where this hurts: when I click this on stage, I have to translate `Control Logic Workbench`, `Scenario Control`, `Diagnosis Snapshot`, `Next Actions`, `engine_running` live into Chinese.
   Suggested mitigation (presentation-friendly): Chinese-first labels on the primary surface; keep English only in muted sublabels.

5. [IMPORTANT] wow_a beats are not explicit
   Stage scenario where this hurts: on `/demo.html` I found generic presets like `着陆展开全链路` and `最大反推`, but nothing marked `BEAT_EARLY / BEAT_DEEP / BEAT_BLOCKED`, so I have to remember the mapping myself.
   Suggested mitigation (presentation-friendly): add a 3-step beat strip with one-click buttons and fixed narration.

6. [IMPORTANT] default tone starts negative
   Stage scenario where this hurts: opening `/demo.html` shows `FAULT` and `未达成` before I intentionally start the story, so the first impression is failure.
   Suggested mitigation (presentation-friendly): default to `就绪 / 点击开始演示`, or auto-load the opening preset.

7. [IMPORTANT] no true demo mode
   Stage scenario where this hurts: there is `初级视图 / 专家视图`, but one stray scroll still exposes JSON, archive path, approval, and file operations.
   Suggested mitigation (presentation-friendly): add `演示模式` that keeps only scene, narration, key state, and one reset action.

## Wow scenarios coverage check

- wow_a: Entry in <10s? N on `/workbench`; only after detouring via `a.workbench-nav-link[href="/demo.html"]`, then `.fan-preset-btn[data-preset="landing-deploy"]` or `.fan-preset-btn[data-preset="max-reverse"]`. On-screen state + narration? Y. Example: "我现在把 TRA 拉到 -32°，L4 已满足，THR_LOCK 已放开，可以进入最大反推。" AI narration fallback visible? N.
- wow_b: Entry in <10s? N; I found no selector or label with `Monte` / `Monte Carlo` on `/workbench` or `/demo.html`. On-screen state + narration? N. AI narration fallback visible? N.
- wow_c: Entry in <10s? N; I found no selector or label with `反向诊断` / `reverse diagnosis`. On-screen state + narration? N; `Diagnosis Snapshot` is a result card, not a presenter flow. AI narration fallback visible? N.

## Anti-bias check

P1 / P2 / P4 / P5 may say the functions exist. My presenter-only finding is the "wrong room" problem: in the first 5 seconds, internal ticketing, split identity, and a default `FAULT` tone damage sponsor confidence before any logic issue appears. That is a stage failure even if the logic is technically correct.

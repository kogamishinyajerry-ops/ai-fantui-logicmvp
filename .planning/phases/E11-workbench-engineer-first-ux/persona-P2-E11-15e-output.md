2026-04-26T03:58:12.424232Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-26T03:58:12.424305Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
Reading additional input from stdin...
OpenAI Codex v0.118.0 (research preview)
--------
workdir: /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
model: gpt-5.4
provider: openai
approval: never
sandbox: danger-full-access
reasoning effort: xhigh
reasoning summaries: none
session id: 019dc7f0-11c9-7353-8494-b73c5a730c4e
--------
user
You are Codex GPT-5.4 acting as **Persona P2 — Senior FCS Engineer & Surface-Inventory Auditor** (Tier-A persona pipeline, E11-15e sub-phase, R1).

Read `.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md` for sub-phase scope, files, and verification baseline.

You ran the E11-15d Tier-B review across 3 rounds (R1, R2, R3) and were the persona who flagged the doc-honesty `last English-only surface` / `uniformly Chinese-first` overclaim. Your enumeration of remaining English-only surfaces in E11-15d's R2 review is what E11-15e set out to close.

## Your specific lens (P2 — Senior FCS Engineer & Surface-Inventory Auditor)

1. **Did E11-15e actually close YOUR list?**
   Cross-reference your E11-15d R2 NIT enumeration against the 22 REWRITE rows in `E11-15e-SURFACE-INVENTORY.md` Section 2. Your R2 listed: `Manual (advisory)`, system options, state-of-world labels, trust-banner body, boot placeholders, reference-packet block. Plus the original R1-D2 IMPORTANT list: `Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`, WOW h3s, topbar chips.
   - For each item on your prior lists, is it now closed (REWRITE in Section 2) or is it explicitly in the deferred Section 3?
   - Are there items you flagged that fell through the cracks (neither closed nor deferred)?

2. **Surface-honesty pledge audit**
   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
   - Any forbidden overclaim phrases (`last English-only surface` / `uniformly Chinese-first` / `all English surfaces` / equivalents) that drifted in?
   - Run the existing E11-15d guard `tests/test_workbench_approval_flow_polish.py::test_e11_15d_artifacts_do_not_overclaim_closure` on a hypothetical extension to E11-15e artifacts — does the SURFACE-INVENTORY language pass that guard's exemption rules?

3. **Out-of-scope deferred list completeness**
   Section 3 lists deferred surfaces but admits the list is "non-exhaustive". Walk `/workbench` HTML once more and find:
   - Any user-visible English-only surface NOT in this PR's REWRITE list AND NOT in Section 3's deferred list. If found, name it (file:line) so it can be added to the deferred list (or reclassified as in-scope).
   - Specific candidates to check: `<span>SW1</span>` / `<span>Logic 1</span>` ... in the circuit panel skeleton; `加载当前工单 · Load Active Ticket` and `快照当前状态 · Snapshot Current State` (already bilingual); the `<pre>Intake -> ...</pre>` flow diagram (Section 3 lists this); `eyebrow` lowercase tags like `probe & trace` (Section 3 lists this); workbench bundle/inbox/approval-center surfaces (off-page or already-bilingual).

4. **Tier classification correctness**
   `E11-15e-SURFACE-INVENTORY.md` Section 1 claims Tier-A based on copy_diff_lines ~38 + 22 REWRITE. Re-count from `git diff main..83d69e4`:
   - copy_diff_lines actual count?
   - REWRITE row count actual?
   - Does the Tier-A trigger fire under the constitutional rule (≥10 lines AND ≥3 REWRITE)? Yes/no with the math.

5. **Persona round-robin succession**
   E11-15d closed with P2 (you, R3 self-signed via Executor-即-Gate v3.2). E11-15e claims P3 as the round-robin lead. `python3 tools/codex_persona_dispatch.py next-persona` returns P3. Verify this is the canonical successor (P1→P2→P3→P4→P5→P1).

## Files to inspect

- `git diff main..83d69e4` (full diff)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` Sections 1, 2, 3, 6
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md`
- `tests/test_workbench_e11_15e_chinese_first_bundle.py` Section 1 (positive bilingual locks — does this list match Section 2 of SURFACE-INVENTORY?)
- `tests/test_workbench_approval_flow_polish.py:182-238` (E11-15d guard, for cross-reference)
- The `/workbench` rendered HTML on a running demo server (Section 6 of new test file uses `_get(server, "/workbench")` — you can grep its assertions for spot checks)

## Out of scope for your lens (other personas cover these)

- P1: engineer-task-flow regression
- P3: bilingual copy quality + convention adherence
- P4: lockstep test contract preservation
- P5: truth-engine red-line + JS-HTML lockstep

## Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

Then list findings with severity tags (`BLOCKER` / `IMPORTANT` / `NIT`), each with `file:line` reference and `Suggested fix:` bullet.

If you find a surface-honesty drift, an overclaim, a missing surface, or a tier-classification error, flag it as `IMPORTANT` minimum.

codex
按 P2 视角做一次只读审计：先恢复 E11-15e 的共享上下文、对比 `main..83d69e4` 的实际 diff、再把你点名的几份工件和 `/workbench` 输出逐项交叉核对。
exec
/bin/zsh -lc "sed -n '1,260p' .planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
# E11-15e — shared context for Tier-A persona prompts

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
**PR:** #30
**HEAD:** `83d69e4`
**Tier:** A (copy_diff_lines ~38, REWRITE rows = 22; per constitution Tier-A iff ≥10 lines AND ≥3 REWRITE)
**Round-robin lead:** P3 (successor of E11-15d's P2)

## What E11-15e ships

Bilingualizes 22 user-visible English-only surfaces on `/workbench` enumerated by P2 during the E11-15d Tier-B review (`tests/test_workbench_approval_flow_polish.py:189-194`).

**Pattern:** `<中文> · <English>` everywhere; English suffix preserved verbatim so prior substring locks (test_workbench_trust_affordance, test_workbench_authority_banner, test_workbench_role_affordance, test_workbench_column_rename, test_workbench_state_of_world_bar) keep passing without contract churn.

## Files in scope

- `src/well_harness/static/workbench.html` — 21 REWRITE strings
- `src/well_harness/static/workbench.js` — 1 lockstep edit at line 3788 (feedback-mode chip dynamic text, both `truth_engine` and `manual_feedback_override` branches bilingualized)
- `tests/test_workbench_e11_15e_chinese_first_bundle.py` — 67 new test cases (positive bilingual locks + stale-English negative guards + English-suffix preservation + structural anchors + JS lockstep + live-served route + truth-engine red-line guard)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` — full surface table + out-of-scope deferred list (Section 3) + truth-engine red line + lockstep impact + persona dispatch plan

## Files explicitly NOT in scope (truth-engine red line)

`controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`, `demo_server.py`. The new lockstep guard `test_e11_15e_does_not_touch_truth_engine_backend` scans these 4 backend files for any of the 23 Chinese display strings introduced in this sub-phase.

## Verification baseline

- 67/67 new tests pass
- 188/188 prior workbench tests pass (lockstep contracts preserved)
- 1221/1221 full suite passes (0 regressions, 35 deselected per default markers)

## Surface honesty pledge

E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.

## Codex degradation contingency

If your account hits secondary-window throttle / token-refresh failure, the project memory rule "Executor 即 Gate (v3.2 治理折叠)" authorizes Claude Code Opus 4.7 to self-sign the Tier-A gate (documented in SURFACE-INVENTORY Section 6). Self-sign requires standard 1221-test green + repo-honesty self-review (already met).

exec
/bin/zsh -lc "sed -n '1,260p' .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '1,260p' .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
# E11 Tier-B Persona Rotation State

> Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger` (governance bundle #2, 2026-04-25, PR #14).
>
> Source of truth for next Tier-B persona selection. Default = round-robin successor (P1 → P2 → P3 → P4 → P5 → P1) of last entry. Owner may write a non-default value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint: written value must NOT equal the immediately preceding Tier-B entry.
>
> New epic (E12, E13, ...) starts a fresh state file with sequence reset to P1.

## Sequence

E11-13: P1 (round-robin start; first Tier-B sub-phase under bundle #2)
E11-14: P2 (round-robin successor; Senior FCS Engineer fits server-side / API contract review)
E11-05: Tier-A (≥10 copy_diff_lines AND ≥3 [REWRITE]: 3 workbench_start.html corrections + 12 ANCHORED card copy lines). All 5 personas dispatched. Rotation pointer unchanged (Tier-A does not consume a Tier-B slot).
E11-03: Tier-A (12 copy_diff_lines, all [REWRITE] — three-column rename in lockstep). All 5 personas dispatched. Rotation pointer unchanged.
E11-04: Tier-B (7 copy_diff_lines, fails ≥10 threshold; though 7 [REWRITE] meets ≥3). Persona = P3 (Demo Presenter — content-fit for domain vocabulary the engineer reads on screen; also the round-robin successor of P2). Plan row 275 said "NO Codex (mechanical relabel)" but the constitution Tier-B rule is the stricter SSOT.
E11-06: Tier-B (10 copy_diff_lines but 0 [REWRITE/DELETE] — all NEW section content fails ≥3 threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit for new endpoint contract validation).
E11-07: Tier-B (4 copy_diff_lines, 0 [REWRITE/DELETE] — pure-NEW banner). Persona = P5 (Apps Engineer — round-robin successor of P4 AND content-fit for customer/repro-facing authority contract messaging).
E11-08: Tier-B (4 copy_diff_lines, 0 [REWRITE/DELETE]). Persona = P1 (Junior FCS Engineer — round-robin wraps P5 → P1 AND content-fit for small UI-only refactor with regression-risk JS attribute reading + URL-param parsing).
E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
E11-15b: Tier-B (7 copy_diff_lines, 7 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P3 (Demo Presenter — round-robin successor of P2 AND content-fit: typography/reading-rhythm/first-glance demo impression is P3's core lens). Bilingualizes h1 + 2 buttons + h2 + approval entry button + caption + h2 to `<中文> · <English>`, preserving English suffixes for dual-route test locks. API remediation message in demo_server.py:743 explicitly preserved (backend contract).
E11-15c: Tier-B (4 copy_diff_lines, 4 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit: this sub-phase rewrites existing test contracts in lockstep with HTML changes, so V&V invariant-preservation lens is exactly right). Direct closure of P3's 2 NITs from E11-15b: (a) page eyebrow `控制逻辑工作台` → `工程师工作区` to break duplication with h1; (b) 3 column h2s flipped from English-first to Chinese-first for full-page direction consistency.
E11-11: Tier-B (0 copy_diff_lines — pure infra + bug fix). Persona = P5 (Apps Engineer — round-robin successor of P4 AND content-fit: P5 reviews end-user-facing reproducibility, browser boot health, and shipped-flow integrity, exactly what the new e2e + bundle-page bug fix needs). Closes deferred JS verification debt from E11-08/13/15c via Playwright smoke suite (8 tests, opt-in `pytest -m e2e`). The first run of the new bundle-page boot test surfaced a latent variable-shadowing bug at workbench.js:1224 (renderFingerprintDocumentList), which is fixed in lockstep along with a sibling shadow at line 1649. Static-source guard test added so the regression is caught even when e2e is deselected.
E11-10: Tier-B (0 copy_diff_lines — pure tooling). Persona = P1 (Junior FCS Engineer — round-robin successor of P5 AND content-fit: small focused tooling with regression-risk concerns (regex parsing, round-robin arithmetic, file-system side-effects) is exactly P1's lens). Adds tools/codex_persona_dispatch.py with 4 subcommands (dispatch / collect / next-persona / append-rotation) and 34 tests covering verdict parser, finding counter, tokens parser, round-robin arithmetic, rotation-state parse + roundtrip, and end-to-end collect.
E11-15d: Tier-B (Persona = P2 — Senior FCS Engineer — round-robin successor of E11-10's P1, derived programmatically by next-persona tool. Bilingualizes the Approval Center lane labels: 3 h3s + 2 lane buttons + 1 pending-lane body copy = 6 [REWRITE]; <10 copy_diff → Tier-B. Persona-content fit: P2's lens on visible-copy consistency for the approval-flow surface. P2 R1 IMPORTANT closure: removed earlier overclaim that this sub-phase finished the workbench Chinese-first thread. Surfaces still English-only after E11-15d: `Hide for session` (trust banner dismiss), `Truth Engine — Read Only` (authority headline), `No proposals submitted yet.` (inbox placeholder), `Pending Kogami sign-off` (affordance strong text), and WOW starter card h3s — deferred to follow-up E11-15e.)
E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.

 succeeded in 0ms:
# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY

**Date:** 2026-04-26
**Status:** in_review (Tier-A, ≥15 REWRITE rows → 5-persona dispatch)
**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
**Scope:** Bilingualize the user-visible English-only surfaces on `/workbench`
that P2 enumerated during the E11-15d Tier-B review (see
`tests/test_workbench_approval_flow_polish.py:189-194`).

---

## 1. Tier classification

Per the constitution, Tier = **Tier-A** iff
`copy_diff_lines ≥ 10 AND (REWRITE + DELETE) count ≥ 3`.

| Metric | Count |
|--------|------:|
| copy_diff_lines (workbench.html + workbench.js)        | ~38 |
| REWRITE rows (display strings rewritten in place)      | **22** |
| DELETE rows (English-only string removed without bilingual replacement) | 0 |
| ADD rows (new strings introduced for the first time)   | 0 |

**Verdict: Tier-A.** Dispatch round-robin successor of E11-15d's P2 → **P3**, plus
P1, P2, P4, P5 per Tier-A 5-persona requirement.

---

## 2. Surface table (REWRITE = 22)

Pattern across all rows: `<中文> · <English>`. The English suffix is preserved
verbatim so prior-sub-phase substring locks (`assert <english> in html`) keep
passing without contract churn.

| # | Surface | File:Line | Old (English-only) | New (bilingual) |
|---|---------|-----------|---------------------|-----------------|
| 1 | Identity chip label | workbench.html:26 | `<span>Identity</span>` | `<span>身份 · Identity</span>` |
| 2 | Ticket chip label | workbench.html:30 | `<span>Ticket</span>` | `<span>工单 · Ticket</span>` |
| 3 | Feedback Mode chip label | workbench.html:41 | `<span>Feedback Mode</span>` | `<span>反馈模式 · Feedback Mode</span>` |
| 4 | Manual (advisory) chip text (HTML) | workbench.html:42 | `<strong>Manual (advisory)</strong>` | `<strong>手动（仅参考）· Manual (advisory)</strong>` |
| 5 | Manual (advisory) chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Manual (advisory)"` literal | `"手动（仅参考）· Manual (advisory)"` |
| 6 | Truth Engine chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Truth Engine"` literal | `"真值引擎 · Truth Engine"` |
| 7 | System chip label | workbench.html:46 | `<span>System</span>` | `<span>系统 · System</span>` |
| 8 | WOW h3 (wow_a) — direction flip | workbench.html:111 | `Causal Chain · 因果链走读` | `因果链走读 · Causal Chain` |
| 9 | WOW h3 (wow_b) — direction flip | workbench.html:143 | `Monte Carlo · 1000-trial 可靠性` | `1000-trial 可靠性 · Monte Carlo` |
| 10 | WOW h3 (wow_c) — direction flip | workbench.html:173 | `Reverse Diagnose · 反向诊断` | `反向诊断 · Reverse Diagnose` |
| 11 | State-of-world label · sha | workbench.html:65 | `truth-engine SHA` | `真值引擎 SHA · truth-engine SHA` |
| 12 | State-of-world label · e2e | workbench.html:71 | `recent e2e` | `最近 e2e · recent e2e` |
| 13 | State-of-world label · adversarial | workbench.html:77 | `adversarial` | `对抗样本 · adversarial` |
| 14 | State-of-world label · open issues | workbench.html:83 | `open issues` | `未关闭问题 · open issues` |
| 15 | State-of-world advisory flag | workbench.html:87 | `advisory · not a live truth-engine reading` | `仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading` |
| 16 | Trust banner scope `<em>` | workbench.html:209-211 | `<em>What "manual feedback" means here:</em> any value...` | `<em>这里"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入...` |
| 17 | Trust banner advisory `<strong>` | workbench.html:213 | `<strong>That mode is advisory.</strong>` | `<strong>该模式仅作参考 · That mode is advisory.</strong>` |
| 18 | Trust banner truth-engine `<span>` | workbench.html:215-217 | `Truth engine readings (logic gates L1–L4 ...)` | `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings ...` |
| 19 | Trust banner dismiss button | workbench.html:225 | `Hide for session` | `隐藏（本次会话）· Hide for session` |
| 20 | Authority banner headline | workbench.html:248 | `Truth Engine — Read Only` | `真值引擎 · 只读 · Truth Engine — Read Only` |
| 21 | Pre-hydration boot status (control panel) | workbench.html:278 | `Waiting for probe & trace panel boot.` | `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` |
| 22 | Pre-hydration boot status (document panel) | workbench.html:298 | `Waiting for annotate & propose panel boot.` | `等待 annotate & propose 面板启动 · Waiting for annotate & propose panel boot.` |
| 23 | Pre-hydration boot status (circuit panel) | workbench.html:318 | `Waiting for hand off & track panel boot.` | `等待 hand off & track 面板启动 · Waiting for hand off & track panel boot.` |
| 24 | Reference packet intro `<p>` | workbench.html:301 | `Reference packet, clarification notes...` | `参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, ...` |
| 25 | Annotation inbox empty state | workbench.html:337 | `<li>No proposals submitted yet.</li>` | `<li>暂无已提交提案 · No proposals submitted yet.</li>` |
| 26 | Pending sign-off `<strong>` | workbench.html:363 | `<strong>Pending Kogami sign-off</strong>` | `<strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>` |

(22 rows after dedup of #5/#6 with their HTML siblings; the table uses 26 row IDs
for line-of-evidence but treats #4+#5 and #11-#14+#15 as single `surface diff`
counts in the metric table above.)

---

## 3. Out of scope (explicitly deferred — surface-honesty closure)

E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
following surfaces remain English-only and are **deferred to future sub-phases
or constitutional decisions**, not silently included:

| Deferred surface | Why deferred | File:Line |
|------------------|--------------|-----------|
| `<option>` system values (`Thrust Reverser`, `Landing Gear`, `Bleed Air Valve`, `C919 E-TRAS`) | Domain proper nouns coupled to value-attribute IDs and the multi-system adapter dispatch in `tests/test_p19_api_multisystem.py`. Bilingualizing the option text would require coordinated changes to value-id parsing, locale-mapping, and the adapter contract. | workbench.html:48-51 |
| Post-hydration JS boot status strings (`Probe & Trace ready. Scenario actions are staged for the next bundle.` × 3) | Locked by `tests/test_workbench_column_rename.py:170-172`; would require workbench.js bilingualization with its own lockstep test contract. **Note:** This is the string users actually see for most of session — the "Waiting for ... panel boot." strings E11-15e bilingualizes are pre-hydration only. Re-tier as Tier-A for a follow-up sub-phase. | workbench.js boot fns |
| `<pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>` | Visual phase-arrow diagram, not English copy. Would require a Chinese arrow notation decision (e.g. `承接 → 澄清 → 回放 → 诊断 → 知识`); deferred to UX/copy decision. | workbench.html:302 |
| `data-wow-id="wow_a"` attribute strings + `data-wow-action="run"` | Internal data-* attributes, not user-visible — out of bilingualization scope by design. | workbench.html:104-194 |
| `wow_a/b/c` tag spans (`<span class="workbench-wow-tag">wow_a</span>`) | Card identifier sigil, not display copy; these literally name the API endpoint group. | workbench.html:110/142/172 |
| Eyebrow `probe & trace` / `annotate & propose` / `hand off & track` (lowercase column eyebrows) | These are paired with the bilingual `<h2>` titles E11-15c shipped (e.g. `<h2>探针与追踪 · Probe & Trace</h2>`). Eyebrows are intentionally English-only for the column-key tag pattern; if revisited, would need its own constitutional pass. | workbench.html:274/294/314 |
| `WB-E06-SHELL` ticket id, `Kogami / Engineer` identity | Identifiers/proper nouns, not display copy. | workbench.html:27/31 |

**Surface-honesty pledge:** This sub-phase closes 22 surfaces. It does NOT close
"all" or "the last". The deferred list above is **non-exhaustive** — if a
reviewer finds another English-only user-visible surface not listed here that is
neither REWRITE in this slice nor in the deferred table, that finding is
**legitimate** and a CHANGES_REQUIRED is appropriate.

---

## 4. Truth-engine red line

Display-copy edits only. `controller.py` / `runner.py` / `models.py` /
`src/well_harness/adapters/` / `demo_server.py` are **untouched**. Lockstep
guard at `tests/test_workbench_e11_15e_chinese_first_bundle.py::
test_e11_15e_does_not_touch_truth_engine_backend` scans backend files for any
of the 23 Chinese display strings introduced here.

---

## 5. Lockstep test impact

| Existing test file | Impact | Reason |
|--------------------|--------|--------|
| `test_workbench_trust_affordance.py` | ✅ no change | All 5 substring locks (`Manual (advisory)`, `Truth engine readings`, `Hide for session`, `What "manual feedback" means here`, `That mode is advisory.`) are preserved as English suffixes. |
| `test_workbench_authority_banner.py` | ✅ no change | `Truth Engine — Read Only` preserved as suffix. |
| `test_workbench_role_affordance.py` | ✅ no change | `Pending Kogami sign-off` preserved as suffix. |
| `test_workbench_column_rename.py` | ✅ no change | Pre-hydration `Waiting for ... panel boot.` substrings preserved as suffixes; post-hydration JS strings unchanged (out of scope). |
| `test_workbench_state_of_world_bar.py` | ✅ no change | `advisory · not a live truth-engine reading` preserved as suffix. |
| `test_workbench_chinese_direction_consistency.py` | ✅ no change | E11-15c column h2 invariant unaffected (no h2 changes). |
| `test_workbench_chinese_h2_button_sweep.py` | ✅ no change | h2/button sweep targets are already-bilingual surfaces. |
| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
| `test_workbench_e11_15e_chinese_first_bundle.py` (new) | ✅ added | 67 tests — positive bilingual locks, stale-English negative guards, English-suffix preservation locks, structural anchors, JS lockstep, live-served route, truth-engine red-line guard. |

Full suite verification: **1221 passed, 0 regressions** (pre-PR baseline 1154).

---

## 6. Persona dispatch plan

Tier-A → 5-persona round-robin. E11-15d closed with P2 → successor for E11-15e
**lead** is **P3**.

| Persona | Lens |
|---------|------|
| P1 | Engineer-task-flow regression |
| P2 | Surface-inventory honesty + closure-claim guards |
| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
| P4 | Lockstep test contract preservation (no churn on existing locks) |
| P5 | Truth-engine red-line + JS-HTML lockstep |

**Codex degradation contingency:** if all 5 codex accounts are
secondary-window-throttled or token-refresh-failed (as in E11-15d R3), apply
**Executor 即 Gate (v3.2 治理折叠)** per the project memory rule:
Claude Code Opus 4.7 self-signs the Tier-A gate, transparently documenting the
fallback in PR body + `dev_handoff.md` + this inventory's persona-rotation
entry. Self-signing requires the standard 1221-test green + repo-honesty self-
review (this inventory + Section 3 surface-honesty pledge satisfy that bar).

exec
/bin/zsh -lc 'pwd && git rev-parse --short HEAD && git status --short && rg -n "E11-15e|E11-15d|LogicMVP|persona|surface-inventory|uniformly Chinese-first|last English-only surface" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
83d69e4
?? .planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-prompt.txt
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-prompt.txt
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-prompt.txt
100:# Task Group: AI FANTUI LogicMVP governance-first audit and Claude Code handoff packaging
103:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s coordination-docs, control-plane drift, and Claude Code handoff workflow, but exact baselines, GitHub settings, and Notion page drift are checkout-specific.
109:- rollout_summaries/2026-04-22T13-49-36-w0BD-claude_code_pivot_report_and_handoff_prompt.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-49-36-019db574-11df-7c20-8119-dc6ee735487d.jsonl, updated_at=2026-04-22T14:31:33+00:00, thread_id=019db574-11df-7c20-8119-dc6ee735487d, governance-first drift audit and coordination package)
119:- rollout_summaries/2026-04-22T13-49-36-w0BD-claude_code_pivot_report_and_handoff_prompt.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-49-36-019db574-11df-7c20-8119-dc6ee735487d.jsonl, updated_at=2026-04-22T14:31:33+00:00, thread_id=019db574-11df-7c20-8119-dc6ee735487d, single copy-paste prompt delivered for Claude Code)
129:- rollout_summaries/2026-04-22T13-49-36-w0BD-claude_code_pivot_report_and_handoff_prompt.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-49-36-019db574-11df-7c20-8119-dc6ee735487d.jsonl, updated_at=2026-04-22T14:31:33+00:00, thread_id=019db574-11df-7c20-8119-dc6ee735487d, factual framing tightened after Claude critique)
160:# Task Group: AI FANTUI LogicMVP C919 E-TRAS reliability simulation candidates and adoption handoff
163:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s C919 E-TRAS workstation and candidate-handoff workflow, but branch names, commit SHAs, Notion pages, and demo URLs are checkout-specific.
169:- rollout_summaries/2026-04-22T04-17-29-5Lxl-c919_etras_reliability_simulation_candidate_handoff.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T12-17-29-019db368-49c2-7091-9813-ac5513754a07.jsonl, updated_at=2026-04-22T04:38:31+00:00, thread_id=019db368-49c2-7091-9813-ac5513754a07, candidate UI shipped on isolated branch after runtime fix)
179:- rollout_summaries/2026-04-22T04-17-29-5Lxl-c919_etras_reliability_simulation_candidate_handoff.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T12-17-29-019db368-49c2-7091-9813-ac5513754a07.jsonl, updated_at=2026-04-22T04:38:31+00:00, thread_id=019db368-49c2-7091-9813-ac5513754a07, Notion/GitHub handoff completed with pushed branch and final fix commit)
328:- ElevenLabs, PVC, voice-cloning, Chinese TTS, 90 分钟中文探店博主语料结构表, VOICE-CORPUS-90MIN-PLAN.md, ELEVENLABS-VOICE-CORPUS-GUIDE.md, MATERIAL-DROPZONE.md, avatar-lab/inputs/persona/voice-pvc, 90-150 分钟, 20-30 分钟, 逛 / 光, pronunciation dictionaries, shop-explainer
338:- ElevenLabs voice-training materials in this project are organized under `avatar-lab/inputs/persona/voice-pvc/`; do not scatter PVC material inside transient job directories [Task 1]
355:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP plus machine-level Claude/Codex config under `~/.claude`, `~/.codex`, `~/.cc-switch`; reuse_rule=safe for local Claude/Codex auth-routing diagnosis on this machine, but treat exact repo-planning references as checkout-specific.
361:- rollout_summaries/2026-04-18T16-09-41-mAqs-claude_official_auth_and_provider_routing_recovery.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/19/rollout-2026-04-19T00-09-41-019da15a-e528-7861-97cf-de68dd62dbf8.jsonl, updated_at=2026-04-19T03:01:02+00:00, thread_id=019da15a-e528-7861-97cf-de68dd62dbf8, useful when Notion MCP or Computer Use is unavailable)
371:- rollout_summaries/2026-04-18T16-09-41-mAqs-claude_official_auth_and_provider_routing_recovery.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/19/rollout-2026-04-19T00-09-41-019da15a-e528-7861-97cf-de68dd62dbf8.jsonl, updated_at=2026-04-19T03:01:02+00:00, thread_id=019da15a-e528-7861-97cf-de68dd62dbf8, partial recovery; auth still blocked by browser-login completion)
842:# Task Group: AI FANTUI LogicMVP autonomous Notion-synced development
844:scope: Continue AI FANTUI LogicMVP automatically from `.planning` and Notion-synced state, keep the control tower current, and use approved/no-review gate state to decide whether to keep moving.
845:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s autonomous GSD + Notion workflow, but exact phase numbers and page text are repo-specific.
851:- rollout_summaries/2026-04-08T15-29-03-VmzV-notion_api_hub_and_p6_sync_timeout_baseline_restore.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/08/rollout-2026-04-08T23-29-03-019d6db6-16ac-7431-9092-63393e7770a3.jsonl, updated_at=2026-04-11T04:03:27+00:00, thread_id=019d6db6-16ac-7431-9092-63393e7770a3, isolated hub and P6 timeout/baseline recovery)
855:- AI FANTUI LogicMVP 控制塔, NOTION_API_KEY, gsd_notion_sync.py, prepare-opus-review, writeback timeout, stronger QA baseline, 175 tests OK, 10 demo smoke scenarios pass, 8/8 shared validation checks pass
861:- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, P7 workbench slices synced with dashboard/status/09C/freeze)
862:- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, P8 runtime-generalization work stayed autonomous through Notion writeback and gate recheck)
872:- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, fingerprint and onboarding boards built from existing payloads)
873:- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, runtime comparison extended existing validation surfaces to 23/23 pass)
899:# Task Group: AI FANTUI LogicMVP demo presentation, launch behavior, and leadership-facing communication
902:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s demo/presentation workflow, but ports, exact UI files, and report docs are checkout-specific.
908:- rollout_summaries/2026-04-07T06-17-29-49ud-well_harness_cockpit_vdt_logicboard_refinement.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T14-17-29-019d6696-c420-7481-af73-35d6f2431385.jsonl, updated_at=2026-04-09T03:18:57+00:00, thread_id=019d6696-c420-7481-af73-35d6f2431385, iterative refinement from user corrections)
909:- rollout_summaries/2026-04-07T06-20-24-tGb4-round_92_direct_vdt_control_flatter_logic_board.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T14-20-24-019d6699-6f65-7712-ba2d-13ed0f64e87e.jsonl, updated_at=2026-04-08T14:50:07+00:00, thread_id=019d6699-6f65-7712-ba2d-13ed0f64e87e, final Round 92 reflow with preserved endpoint contracts)
919:- rollout_summaries/2026-04-10T06-34-44-9twF-rewrite_material_and_start_ui.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/10/rollout-2026-04-10T14-34-44-019d7619-a293-7681-baa7-381fd6276d45.jsonl, updated_at=2026-04-12T05:24:57+00:00, thread_id=019d7619-a293-7681-baa7-381fd6276d45, material rewrite plus local UI launch)
929:- rollout_summaries/2026-04-10T06-34-44-9twF-rewrite_material_and_start_ui.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/10/rollout-2026-04-10T14-34-44-019d7619-a293-7681-baa7-381fd6276d45.jsonl, updated_at=2026-04-12T05:24:57+00:00, thread_id=019d7619-a293-7681-baa7-381fd6276d45, `8000` conflict handled by switching to `8001`)
930:- rollout_summaries/2026-04-07T06-17-29-49ud-well_harness_cockpit_vdt_logicboard_refinement.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T14-17-29-019d6696-c420-7481-af73-35d6f2431385.jsonl, updated_at=2026-04-09T03:18:57+00:00, thread_id=019d6696-c420-7481-af73-35d6f2431385, stable demo launch path on `8770`)
940:- rollout_summaries/2026-04-08T15-04-09-7j1J-reconstruct_ai_coding_development_log_and_leadership_speech.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/08/rollout-2026-04-08T23-04-09-019d6d9f-4dc6-7bb3-9d6b-c6e48273fbbf.jsonl, updated_at=2026-04-08T15:12:08+00:00, thread_id=019d6d9f-4dc6-7bb3-9d6b-c6e48273fbbf, detailed Chinese summary and 5-minute leadership speech)
950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
951:- rollout_summaries/2026-04-07T05-30-48-VWde-thrust_reverser_harness_audit_and_control_freeze.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T13-30-48-019d666c-0536-7403-80c3-1216c53a4944.jsonl, updated_at=2026-04-08T08:22:56+00:00, thread_id=019d666c-0536-7403-80c3-1216c53a4944, frozen controller truth and simplified-plant caveat)
1678:- Official Claude cloud-local handoff is not a one-click sync of local Claude Code sessions/memory/`.claude` config; the practical route is GitHub repo + Claude Project / GitHub integration / Claude Code on the web, with project rules separated from personal machine config [Task 3]

codex
这轮是只读 code review，我会按 `gsd-code-review` 的 findings-first 约束执行，并把 P2 关心的 closure list、overclaim guard、deferred completeness、Tier 计数、persona 轮转五件事分开核对。
exec
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.codex/skills/gsd-code-review/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
sed: /Users/Zhuanz/.codex/skills/gsd-code-review/SKILL.md: No such file or directory

exec
/bin/zsh -lc "sed -n '160,260p' tests/test_workbench_approval_flow_polish.py && printf '\\n---\\n' && sed -n '1,260p' tests/test_workbench_e11_15e_chinese_first_bundle.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:

def test_e11_15d_does_not_touch_api_remediation_message() -> None:
    """The 409 remediation message is API contract, not display copy."""
    repo_root = Path(__file__).resolve().parents[1]
    demo_server = (repo_root / "src" / "well_harness" / "demo_server.py").read_text(
        encoding="utf-8"
    )
    assert (
        "Acquire sign-off via Approval Center, or switch to auto_scrubber."
        in demo_server
    )
    # Approval-flow Chinese strings must NOT leak into backend
    new_strings = [
        "待审", "通过 · Accept", "驳回 · Reject",
        "通过提案", "驳回提案", "已提交的标注提案",
    ]
    for new_string in new_strings:
        assert new_string not in demo_server, (
            f"E11-15d Chinese {new_string!r} unexpectedly leaked into demo_server.py"
        )


# ─── 7. P2 R1 IMPORTANT closure: surface inventory honesty guard ─────


def test_e11_15d_artifacts_do_not_overclaim_closure() -> None:
    """P2 R1 + R2 IMPORTANT closure: earlier drafts of the E11-15d
    SURFACE-INVENTORY, the PERSONA-ROTATION-STATE entry, and this test
    module's docstring all claimed `last English-only surface` and/or
    `uniformly Chinese-first`. P2 verified `/workbench` still has many
    English-only surfaces outside this slice (`Hide for session`,
    `Truth Engine — Read Only`, `No proposals submitted yet.`,
    `Pending Kogami sign-off`, WOW h3s, topbar chips, state-of-world
    labels, etc.). All three artifacts were corrected to defer those
    to E11-15e. This guard scans ALL three artifacts to prevent the
    overclaim from being reintroduced silently in any of them.
    """
    repo_root = Path(__file__).resolve().parents[1]
    artifacts = [
        repo_root
        / ".planning"
        / "phases"
        / "E11-workbench-engineer-first-ux"
        / "E11-15d-SURFACE-INVENTORY.md",
        repo_root
        / ".planning"
        / "phases"
        / "E11-workbench-engineer-first-ux"
        / "PERSONA-ROTATION-STATE.md",
        # Self-scan: this test file's own docstring header is included.
        Path(__file__),
    ]
    forbidden_overclaims = [
        "last English-only surface",
        "uniformly Chinese-first",
    ]
    for artifact in artifacts:
        text = artifact.read_text(encoding="utf-8")
        for phrase in forbidden_overclaims:
            # The forbidden phrase is a CLAIM problem, not a literal-mention
            # problem. Exempt lines where the phrase appears inside a quoted
            # context (Markdown blockquote, backticks anywhere on line, or
            # double-quotes anywhere on line) — those are literal references
            # to the phrase, not fresh assertions of the claim. Bare unquoted
            # mentions still fail the guard.
            for line_no, line in enumerate(text.splitlines(), 1):
                if phrase not in line:
                    continue
                if line.lstrip().startswith(">"):
                    continue
                # If the line carries any quote or backtick, the phrase is
                # most likely being referenced as a literal historical note,
                # not asserted as a fresh claim.
                if "`" in line or '"' in line:
                    continue
                raise AssertionError(
                    f"{artifact.name}:{line_no} contains forbidden overclaim "
                    f"phrase {phrase!r}: {line!r}"
                )

---
"""E11-15e — Tier-A Chinese-first bundle regression lock.

Bilingualizes 17 user-visible English-only surfaces enumerated by P2
during the E11-15d review (see test_workbench_approval_flow_polish.py
docstring Section 7 + .planning/phases/E11-workbench-engineer-first-ux/
E11-15d-SURFACE-INVENTORY.md):

  Topbar chips (5):       身份/工单/反馈模式/系统 + Manual (advisory) chip
  WOW h3 direction (3):   Causal Chain / Monte Carlo / Reverse Diagnose
  State-of-world (5):     truth-engine SHA / recent e2e / adversarial /
                          open issues / advisory flag
  Trust banner body (3):  scope <em>, advisory <strong>, truth-engine <span>
  Authority banner (1):   Truth Engine — Read Only headline
  Trust dismiss (1):      Hide for session button
  Boot placeholders (3):  pre-hydration "Waiting for ... panel boot."
  Reference packet (1):   Annotate column intro <p>
  Inbox empty (1):        No proposals submitted yet.
  Pending sign-off (1):   Pending Kogami sign-off

Pattern: `<中文> · <English>` everywhere; English suffix is preserved
verbatim so all prior `assert <english> in html` substring locks across
test_workbench_trust_affordance, test_workbench_authority_banner,
test_workbench_role_affordance, test_workbench_column_rename, and
test_workbench_state_of_world_bar continue to pass without contract
churn.

Out of scope (deferred to a future Tier-A or constitutional decision):
  - <option> system values (`Thrust Reverser`, `Landing Gear`, etc.) —
    domain proper nouns coupled to value-attribute IDs and to the
    multi-system adapter dispatch in tests/test_p19_api_multisystem.py.
  - Post-hydration JS boot status strings (`Probe & Trace ready. ...`)
    locked by tests/test_workbench_column_rename.py:170-172 — those are
    a separate JS-side bilingualization with their own lockstep contract.
  - <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge
    </pre> flow diagram — visual phase-arrow, not English copy.
  - Workbench-bundle / approval-center / annotation-toolbar surfaces
    that were already bilingualized in earlier sub-phases.

Test-tier rationale: ≥15 REWRITE strings → Tier-A per the constitution.
"""

from __future__ import annotations

import http.client
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import DemoRequestHandler


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"


def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request("GET", path)
    response = connection.getresponse()
    return response.status, response.read().decode("utf-8")


@pytest.fixture
def server():
    s, t = _start_demo_server()
    try:
        yield s
    finally:
        s.shutdown()
        s.server_close()
        t.join(timeout=2)


# ─── 1. Bilingualized strings POSITIVELY locked ──────────────────────


@pytest.mark.parametrize(
    "bilingual",
    [
        # Topbar chip labels (5)
        "<span>身份 · Identity</span>",
        "<span>工单 · Ticket</span>",
        "<span>反馈模式 · Feedback Mode</span>",
        "<span>系统 · System</span>",
        "<strong>手动（仅参考）· Manual (advisory)</strong>",
        # WOW h3 direction flips (3) — Chinese-first per E11-15c convention
        '<h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>',
        '<h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>',
        '<h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>',
        # State-of-world labels (4) + advisory flag (1)
        "真值引擎 SHA · truth-engine SHA",
        "最近 e2e · recent e2e",
        "对抗样本 · adversarial",
        "未关闭问题 · open issues",
        "仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading",
        # Trust banner body (3)
        '这里"手动反馈"的含义 · What "manual feedback" means here:',
        "该模式仅作参考 · That mode is advisory.",
        "真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings",
        # Trust banner dismiss (1)
        "隐藏（本次会话）· Hide for session",
        # Authority banner headline (1)
        "真值引擎 · 只读 · Truth Engine — Read Only",
        # Pre-hydration boot placeholders (3)
        "等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.",
        "等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.",
        "等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot.",
        # Reference-packet intro (1)
        "参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes",
        # Inbox empty state (1)
        "暂无已提交提案 · No proposals submitted yet.",
        # Pending sign-off (1)
        "等待 Kogami 签字 · Pending Kogami sign-off",
    ],
)
def test_workbench_html_carries_bilingual_e11_15e_string(bilingual: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert bilingual in html, f"missing E11-15e bilingual string: {bilingual}"


# ─── 2. Stale English-only surfaces are gone ─────────────────────────


@pytest.mark.parametrize(
    "stale",
    [
        # Bare topbar chip labels (no Chinese prefix) — must be replaced
        "<span>Identity</span>",
        "<span>Ticket</span>",
        "<span>Feedback Mode</span>",
        "<span>System</span>",
        "<strong>Manual (advisory)</strong>",
        # WOW h3 stale English-first ordering (E11-15c convention)
        '<h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>',
        '<h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>',
        '<h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>',
        # Bare state-of-world labels (no Chinese prefix)
        ">truth-engine SHA<",
        ">recent e2e<",
        ">adversarial<",
        ">open issues<",
        # Bare trust-banner body lines — these are now sentence-internal
        # so we look for the line-leading position they used to hold.
        "<em>What \"manual feedback\" means here:</em>",
        "<strong>That mode is advisory.</strong>",
        # Bare button + headline + boot placeholders
        ">\n          Hide for session\n        <",
        ">\n          Truth Engine — Read Only\n        <",
        ">\n            Waiting for probe &amp; trace panel boot.\n          <",
        ">\n            Waiting for annotate &amp; propose panel boot.\n          <",
        ">\n            Waiting for hand off &amp; track panel boot.\n          <",
        # Bare inbox + pending sign-off
        "<li>No proposals submitted yet.</li>",
        "<strong>Pending Kogami sign-off</strong>",
    ],
)
def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert stale not in html, f"stale English-only surface still present: {stale}"


# ─── 3. English suffixes preserved (substring locks unchanged) ───────


@pytest.mark.parametrize(
    "preserved_english_suffix",
    [
        # Anchors required by trust_affordance.py
        "Manual (advisory)",
        "Truth engine readings",
        "Hide for session",
        'What "manual feedback" means here',
        "That mode is advisory.",
        # Anchor required by authority_banner.py
        "Truth Engine — Read Only",
        # Anchor required by role_affordance.py
        "Pending Kogami sign-off",
        # Anchor required by state_of_world_bar.py
        "advisory · not a live truth-engine reading",
        # Anchors required by column_rename.py:118-120 (pre-hydration)
        "Waiting for probe &amp; trace panel boot.",
        "Waiting for annotate &amp; propose panel boot.",
        "Waiting for hand off &amp; track panel boot.",
    ],
)
def test_e11_15e_preserves_english_suffix_locks(preserved_english_suffix: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert preserved_english_suffix in html, (
        f"E11-15e broke English-suffix substring lock: {preserved_english_suffix}"
    )


# ─── 4. Structural anchors preserved ─────────────────────────────────


@pytest.mark.parametrize(
    "anchor",
    [
        'id="workbench-feedback-mode"',
        'id="workbench-trust-banner"',
        'id="workbench-authority-banner"',
        'id="workbench-pending-signoff-affordance"',
        'id="workbench-state-of-world-bar"',
        'id="workbench-wow-starters"',
        'data-trust-banner-dismiss',
        'data-feedback-mode="manual_feedback_override"',
    ],
)
def test_e11_15e_preserves_structural_anchors(anchor: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert anchor in html, f"E11-15e broke structural anchor: {anchor}"


# ─── 5. workbench.js feedback-mode chip stays in lockstep with HTML ──


def test_workbench_js_feedback_mode_label_is_bilingualized() -> None:
    """workbench.js:3788 dynamically rewrites the chip <strong> on mode
    switch. If the JS literal stays English-only, the very first mode
    flip would silently revert the static HTML's bilingual chip back to
    `Manual (advisory)` / `Truth Engine`. Lock both branches."""
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert '"真值引擎 · Truth Engine"' in js, (
        "JS feedback-mode `truth_engine` branch must use bilingual label"
    )
    assert '"手动（仅参考）· Manual (advisory)"' in js, (
        "JS feedback-mode `manual_feedback_override` branch must use bilingual label"
    )
    # Stale English-only literals must not coexist (would imply duplicate
    # write-paths or stale residue).
    assert '"Truth Engine"' not in js, (
        'stale English-only `"Truth Engine"` literal still in workbench.js'
    )
    assert '"Manual (advisory)"' not in js, (
        'stale English-only `"Manual (advisory)"` literal still in workbench.js'
    )


# ─── 6. Live-served route reflects E11-15e end-to-end ────────────────


def test_workbench_route_serves_e11_15e_bundle(server) -> None:
    status, html = _get(server, "/workbench")
    assert status == 200
    # Spot-check one string from each surface category.
    assert "身份 · Identity" in html
    assert "因果链走读 · Causal Chain" in html
    assert "真值引擎 SHA · truth-engine SHA" in html
    assert "该模式仅作参考 · That mode is advisory." in html
    assert "隐藏（本次会话）· Hide for session" in html
    assert "真值引擎 · 只读 · Truth Engine — Read Only" in html

exec
/bin/zsh -lc 'rg -n "last English-only surface|uniformly Chinese-first|all English surfaces|all English-only|uniformly|the last|Chinese-first" -S .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md tests/test_workbench_e11_15e_chinese_first_bundle.py .planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md .planning/phases/E11-workbench-engineer-first-ux/persona-P*-E11-15e-output.md .planning/phases/E11-workbench-engineer-first-ux/persona-P*-E11-15e-prompt.txt src/well_harness/static/workbench.html src/well_harness/static/workbench.js' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
tests/test_workbench_e11_15e_chinese_first_bundle.py:1:"""E11-15e — Tier-A Chinese-first bundle regression lock.
tests/test_workbench_e11_15e_chinese_first_bundle.py:95:        # WOW h3 direction flips (3) — Chinese-first per E11-15c convention
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:1:# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:72:E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:87:"all" or "the last". The deferred list above is **non-exhaustive** — if a
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:115:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:131:| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:35:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-prompt.txt:28:   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:9:1. **Convention adherence — Chinese-first ordering**
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:10:   - E11-15c established Chinese-first column h2 ordering. Are E11-15e's WOW h3 direction flips (`因果链走读 · Causal Chain` / `1000-trial 可靠性 · Monte Carlo` / `反向诊断 · Reverse Diagnose`) consistent with E11-15c?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:11:   - Are all 22 REWRITE strings Chinese-first (Chinese before middle dot)?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:12:   - Is `1000-trial 可靠性 · Monte Carlo` actually "Chinese-first" given the leading "1000-trial" English token? Should it be re-ordered as `可靠性 1000-trial · Monte Carlo` or `1000 次试验可靠性 · Monte Carlo` for stricter convention adherence?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:32:   - E11-15c flipped column h2s from English-first to Chinese-first. E11-15e flips WOW h3s the same way. But the WOW h3s previously had a different convention — original was English-first. Verify the flip is consistent with the **page-wide direction convention**, not breaking some special case.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-prompt.txt:22:   - The WOW starter cards' h3 changed from English-first to Chinese-first ordering. Does this affect screen-reader announcement order for the `aria-labelledby` linkage (workbench-wow-a-title etc.)? The h3 is the labelled-by target — the rest of the card description still starts with the API endpoint string.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-prompt.txt:25:   - The new `等待 Kogami 签字 · Pending Kogami sign-off` is followed by an existing Chinese-first body span: `你的提案已加入排队，等待 Kogami 处理...`. Does the doubled "等待 Kogami" reading (header + body) feel redundant, or is it OK reinforcement?
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:43:   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:5:You ran the E11-15d Tier-B review across 3 rounds (R1, R2, R3) and were the persona who flagged the doc-honesty `last English-only surface` / `uniformly Chinese-first` overclaim. Your enumeration of remaining English-only surfaces in E11-15d's R2 review is what E11-15e set out to close.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:15:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:16:   - Any forbidden overclaim phrases (`last English-only surface` / `uniformly Chinese-first` / `all English surfaces` / equivalents) that drifted in?
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:37:   - The WOW starter cards' h3 changed from English-first to Chinese-first ordering. Does this affect screen-reader announcement order for the `aria-labelledby` linkage (workbench-wow-a-title etc.)? The h3 is the labelled-by target — the rest of the card description still starts with the API endpoint string.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:40:   - The new `等待 Kogami 签字 · Pending Kogami sign-off` is followed by an existing Chinese-first body span: `你的提案已加入排队，等待 Kogami 处理...`. Does the doubled "等待 Kogami" reading (header + body) feel redundant, or is it OK reinforcement?
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:166:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:20:You ran the E11-15d Tier-B review across 3 rounds (R1, R2, R3) and were the persona who flagged the doc-honesty `last English-only surface` / `uniformly Chinese-first` overclaim. Your enumeration of remaining English-only surfaces in E11-15d's R2 review is what E11-15e set out to close.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:30:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:31:   - Any forbidden overclaim phrases (`last English-only surface` / `uniformly Chinese-first` / `all English surfaces` / equivalents) that drifted in?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:111:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:140:E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:142:E11-15c: Tier-B (4 copy_diff_lines, 4 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit: this sub-phase rewrites existing test contracts in lockstep with HTML changes, so V&V invariant-preservation lens is exactly right). Direct closure of P3's 2 NITs from E11-15b: (a) page eyebrow `控制逻辑工作台` → `工程师工作区` to break duplication with h1; (b) 3 column h2s flipped from English-first to Chinese-first for full-page direction consistency.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:145:E11-15d: Tier-B (Persona = P2 — Senior FCS Engineer — round-robin successor of E11-10's P1, derived programmatically by next-persona tool. Bilingualizes the Approval Center lane labels: 3 h3s + 2 lane buttons + 1 pending-lane body copy = 6 [REWRITE]; <10 copy_diff → Tier-B. Persona-content fit: P2's lens on visible-copy consistency for the approval-flow surface. P2 R1 IMPORTANT closure: removed earlier overclaim that this sub-phase finished the workbench Chinese-first thread. Surfaces still English-only after E11-15d: `Hide for session` (trust banner dismiss), `Truth Engine — Read Only` (authority headline), `No proposals submitted yet.` (inbox placeholder), `Pending Kogami sign-off` (affordance strong text), and WOW starter card h3s — deferred to follow-up E11-15e.)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:146:E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:149:# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:220:E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:235:"all" or "the last". The deferred list above is **non-exhaustive** — if a
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:263:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:279:| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:292:/bin/zsh -lc 'pwd && git rev-parse --short HEAD && git status --short && rg -n "E11-15e|E11-15d|LogicMVP|persona|surface-inventory|uniformly Chinese-first|last English-only surface" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:24:1. **Convention adherence — Chinese-first ordering**
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:25:   - E11-15c established Chinese-first column h2 ordering. Are E11-15e's WOW h3 direction flips (`因果链走读 · Causal Chain` / `1000-trial 可靠性 · Monte Carlo` / `反向诊断 · Reverse Diagnose`) consistent with E11-15c?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:26:   - Are all 22 REWRITE strings Chinese-first (Chinese before middle dot)?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:27:   - Is `1000-trial 可靠性 · Monte Carlo` actually "Chinese-first" given the leading "1000-trial" English token? Should it be re-ordered as `可靠性 1000-trial · Monte Carlo` or `1000 次试验可靠性 · Monte Carlo` for stricter convention adherence?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:47:   - E11-15c flipped column h2s from English-first to Chinese-first. E11-15e flips WOW h3s the same way. But the WOW h3s previously had a different convention — original was English-first. Verify the flip is consistent with the **page-wide direction convention**, not breaking some special case.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:200:/bin/zsh -lc 'rg -n "E11-15e|LogicMVP|bilingual|Chinese-first|workbench" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:354:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:363:# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:434:E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:449:"all" or "the last". The deferred list above is **non-exhaustive** — if a
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:477:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:493:| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:508:"""E11-15e — Tier-A Chinese-first bundle regression lock.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:602:        # WOW h3 direction flips (3) — Chinese-first per E11-15c convention
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1342:/bin/zsh -lc 'rg -n "E11-15c|Chinese-first|direction" .planning/phases/E11-workbench-engineer-first-ux tests src/well_harness/static/workbench.html' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1344:tests/test_workbench_column_rename.py:64:        # E11-15c flipped to Chinese-first to match the rest of the page;
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1345:tests/test_workbench_column_rename.py:231:    # E11-15c flipped these from English-first to Chinese-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1346:tests/test_workbench_approval_flow_polish.py:8:This is one slice in a multi-sub-phase Chinese-first thread; it does
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1347:tests/test_workbench_approval_flow_polish.py:9:NOT finish the workbench Chinese-first work. P2 R2 IMPORTANT closure:
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1348:tests/test_workbench_approval_flow_polish.py:189:    `uniformly Chinese-first`. P2 verified `/workbench` still has many
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1349:tests/test_workbench_approval_flow_polish.py:214:        "uniformly Chinese-first",
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1350:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:6:> body copy (6 strings). Note: this is NOT the final Chinese-first
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1351:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1352:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:78:## Workbench Chinese-first thread progress (NOT closure)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1353:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:80:E11-15d is one slice in a multi-sub-phase Chinese-first thread:
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1357:tests/test_workbench_e11_15e_chinese_first_bundle.py:1:"""E11-15e — Tier-A Chinese-first bundle regression lock.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1359:tests/test_workbench_e11_15e_chinese_first_bundle.py:95:        # WOW h3 direction flips (3) — Chinese-first per E11-15c convention
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1364:tests/test_workbench_chinese_eyebrow_sweep.py:1:"""E11-15 — Chinese-first eyebrow sweep.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1365:tests/test_workbench_chinese_eyebrow_sweep.py:5:reads Chinese-first at a glance. The 3 column-eyebrows (probe & trace,
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1366:tests/test_workbench_chinese_eyebrow_sweep.py:8:each already provides Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1368:tests/test_workbench_chinese_eyebrow_sweep.py:72:    assert eyebrow_html in html, f"missing Chinese-first eyebrow: {eyebrow_html}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1369:tests/test_workbench_chinese_eyebrow_sweep.py:121:        # h1 main title is bilingualized by E11-15b (Chinese-first); the
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1371:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:1:# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1377:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:115:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1378:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:131:| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1379:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:45:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1381:.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md:7:> (Chinese-first DOM render). The new e2e infra immediately surfaced a
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1384:.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md:86:- Real-DOM control-panel + approval entry buttons render Chinese-first text.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1396:tests/test_workbench_chinese_direction_consistency.py:1:"""E11-15c — Chinese-first direction consistency + h1/eyebrow dedup.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1399:tests/test_workbench_chinese_direction_consistency.py:13:    while the rest of the page is Chinese-first. E11-15c flips them
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1401:tests/test_workbench_chinese_direction_consistency.py:62:# ─── 1. NIT #2: column h2s are now Chinese-first ─────────────────────
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1402:tests/test_workbench_chinese_direction_consistency.py:75:    assert chinese_first_h2 in html, f"missing Chinese-first column h2: {chinese_first_h2}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1409:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:44:E11-15c closure (2 tests): real-DOM headers + buttons all render Chinese-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1413:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:379:92af49a phase(E11-15b): Chinese-first iter 2 — h1/h2/buttons/caption bilingualized (#25)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1414:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:492:+- E11-15c (Chinese-first DOM rendering — only HTML-string assertions
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1415:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:638:+# ─── E11-15c closure: Chinese-first DOM render (2 tests) ─────────────
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1416:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:644:+    Chinese-first across every header surface."""
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1418:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:665:+    # column h2s: Chinese-first per E11-15c
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1437:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:3503:     7	- E11-15c (Chinese-first DOM rendering — only HTML-string assertions
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1438:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:3649:   153	# ─── E11-15c closure: Chinese-first DOM render (2 tests) ─────────────
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1439:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:3655:   159	    Chinese-first across every header surface."""
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1441:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:3676:   180	    # column h2s: Chinese-first per E11-15c
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1444:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-prompt.txt:3:# Context — E11-15 Chinese-first eyebrow sweep
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1445:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-prompt.txt:12:5 eyebrow labels above non-bilingual h1/h2s flipped from English-lowercase to pure Chinese so the page reads Chinese-first at a glance:
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1446:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-prompt.txt:22:The 3 column-trio eyebrows (`probe & trace` / `annotate & propose` / `hand off & track`) are intentionally preserved — they live above bilingual h2 titles which already provide Chinese-first signal at the h2 line, and they are positively locked by `tests/test_workbench_column_rename.py`. E11-15 explicitly does NOT touch them.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1447:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-prompt.txt:34:- **Visible-copy consistency**: do the 5 new Chinese strings work harmoniously with their surrounding h1/h2/body copy? Is the page a coherent Chinese-first read, or does any eyebrow read awkwardly against its neighbors?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1448:tests/test_workbench_chinese_h2_button_sweep.py:1:"""E11-15b — Chinese-first h2 / button / caption sweep (iter 2).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1449:tests/e2e/test_workbench_js_boot_smoke.py:7:- E11-15c (Chinese-first DOM rendering — only HTML-string assertions
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1450:tests/e2e/test_workbench_js_boot_smoke.py:160:# ─── E11-15c closure: Chinese-first DOM render (2 tests) ─────────────
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1451:tests/e2e/test_workbench_js_boot_smoke.py:166:    Chinese-first across every header surface."""
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1453:tests/e2e/test_workbench_js_boot_smoke.py:187:    # column h2s: Chinese-first per E11-15c
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1465:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-prompt.txt:22:   - The WOW starter cards' h3 changed from English-first to Chinese-first ordering. Does this affect screen-reader announcement order for the `aria-labelledby` linkage (workbench-wow-a-title etc.)? The h3 is the labelled-by target — the rest of the card description still starts with the API endpoint string.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1466:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-prompt.txt:25:   - The new `等待 Kogami 签字 · Pending Kogami sign-off` is followed by an existing Chinese-first body span: `你的提案已加入排队，等待 Kogami 处理...`. Does the doubled "等待 Kogami" reading (header + body) feel redundant, or is it OK reinforcement?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1467:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:60:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1470:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:18:# Context — E11-15 Chinese-first eyebrow sweep
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1471:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:27:5 eyebrow labels above non-bilingual h1/h2s flipped from English-lowercase to pure Chinese so the page reads Chinese-first at a glance:
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1472:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:37:The 3 column-trio eyebrows (`probe & trace` / `annotate & propose` / `hand off & track`) are intentionally preserved — they live above bilingual h2 titles which already provide Chinese-first signal at the h2 line, and they are positively locked by `tests/test_workbench_column_rename.py`. E11-15 explicitly does NOT touch them.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1473:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:49:- **Visible-copy consistency**: do the 5 new Chinese strings work harmoniously with their surrounding h1/h2/body copy? Is the page a coherent Chinese-first read, or does any eyebrow read awkwardly against its neighbors?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1475:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:350:"""E11-15 — Chinese-first eyebrow sweep.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1476:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:354:reads Chinese-first at a glance. The 3 column-eyebrows (probe & trace,
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1477:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:357:each already provides Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1478:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:418:    assert eyebrow_html in html, f"missing Chinese-first eyebrow: {eyebrow_html}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1479:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1167:     1	"""E11-15 — Chinese-first eyebrow sweep.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1480:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1171:     5	reads Chinese-first at a glance. The 3 column-eyebrows (probe & trace,
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1481:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1174:     8	each already provides Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1482:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1235:    69	    assert eyebrow_html in html, f"missing Chinese-first eyebrow: {eyebrow_html}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1483:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1737:# E11-15 Surface Inventory — Chinese-first eyebrow sweep
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1484:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1747:provides Chinese-first signal at the h2 line and is intentionally
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1485:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1754:reads Chinese-first across every section header. The h1/h2 strings
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1486:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1772:  already gives Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1487:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1843:+E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1499:.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:1:# E11-15 Surface Inventory — Chinese-first eyebrow sweep
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1500:.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:11:provides Chinese-first signal at the h2 line and is intentionally
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1501:.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:18:reads Chinese-first across every section header. The h1/h2 strings
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1502:.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:36:  already gives Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1505:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1024:    19	E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1506:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1026:    21	E11-15c: Tier-B (4 copy_diff_lines, 4 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit: this sub-phase rewrites existing test contracts in lockstep with HTML changes, so V&V invariant-preservation lens is exactly right). Direct closure of P3's 2 NITs from E11-15b: (a) page eyebrow `控制逻辑工作台` → `工程师工作区` to break duplication with h1; (b) 3 column h2s flipped from English-first to Chinese-first for full-page direction consistency.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1509:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-prompt.txt:29:E11-15c closure (2 tests): real-DOM headers + buttons all render Chinese-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1511:.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md:1:# E11-15b Surface Inventory — Chinese-first h2/button/caption sweep (iter 2)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1512:.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md:8:> uniformly Chinese-first while preserving English suffixes for existing
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1527:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:13:| #2: column h2s are still English-first while the rest of the page is Chinese-first | 3 column h2s flipped from `<English> · <中文>` to `<中文> · <English>` for full-page direction consistency |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1528:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:27:  to expect Chinese-first column h2s (param values + live-route check).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1531:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:59:1. 3 column h2s positively asserted Chinese-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1534:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:27:Closes the LAST English-only surface in the workbench demo. With this sub-phase, `/workbench` is uniformly Chinese-first; only the backend API remediation message in `demo_server.py:743` stays English (backend contract, locked by `tests/test_lever_snapshot_manual_override_guard.py:151`).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1535:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:48:- **Visible-copy consistency**: do the 6 new bilingual approval-flow strings work harmoniously with the surrounding E11-15b approval-center surface (`Kogami 提案审批 · Kogami Proposal Triage` h2, `审批中心 · Approval Center` entry button, `审批操作仅限 Kogami · ...` caption)? Does the page now read uniformly as a Chinese-first FCS engineer's approval workflow?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1536:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:53:- **Closure claim verification**: I claim `/workbench` is now uniformly Chinese-first. Verify by `grep -nE ">[A-Za-z][^<]*</h[1-3]>|>[A-Za-z][^<]*</button>"` on `workbench.html` to confirm no remaining English-only h1/h2/h3/button content. Acceptable exceptions: identifier strings in topbar chips (`Identity`, `Ticket`, `System`, `Feedback Mode`), system option labels (`Thrust Reverser`, etc.) which are domain proper-nouns, and the `eyebrow` decorative labels in the column trio (locked by E11-03 tests).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1537:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:67:- **Column-trio eyebrows** — locked by E11-03; bilingual h2 already gives Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1539:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1021:I’ve reached the closure-claim pass. There is already a possible gap outside the approval-center slice: `workbench.html` still appears to have at least one unrelated English-only button label, so I’m verifying that directly with the exact grep pattern and then live-probing `/workbench` through the server to separate “approval-flow done” from “entire page fully Chinese-first.”
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1540:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1541:    76	With E11-15d, the entire `/workbench` UI is uniformly Chinese-first:
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1542:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1572:    19	E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1543:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1574:    21	E11-15c: Tier-B (4 copy_diff_lines, 4 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit: this sub-phase rewrites existing test contracts in lockstep with HTML changes, so V&V invariant-preservation lens is exactly right). Direct closure of P3's 2 NITs from E11-15b: (a) page eyebrow `控制逻辑工作台` → `工程师工作区` to break duplication with h1; (b) 3 column h2s flipped from English-first to Chinese-first for full-page direction consistency.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1544:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1577:    24	E11-15d: Tier-B (Persona = P2 — Senior FCS Engineer — round-robin successor of E11-10's P1 (derived programmatically by next-persona tool). Closes the last English-only surface in the workbench demo (3 approval lane h3s + 2 lane buttons + 1 pending-lane body copy). 6 [REWRITE], <10 copy_diff → Tier-B. Persona-content fit: P2's lens on visible-copy consistency works for this final approval-flow surface. With this sub-phase, /workbench is uniformly Chinese-first — only backend API remediation message in demo_server.py:743 stays English (backend contract).)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1545:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1828:I’ve got enough to separate the copy slice from the stronger marketing claim. I’m running the existing approval-center contract test alongside the new polish tests once, so the final verdict can distinguish “this diff is mechanically safe” from “the page-wide Chinese-first closure claim is still not true.”
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1546:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1900:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1547:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1901:- IMPORTANT `tests/test_workbench_approval_flow_polish.py:1-15`, `tests/test_workbench_approval_flow_polish.py:61-169`, `src/well_harness/static/workbench.html:111`, `src/well_harness/static/workbench.html:143`, `src/well_harness/static/workbench.html:173`, `src/well_harness/static/workbench.html:219-226`: test coverage matches the six-string approval-center polish, not the stronger page-wide closure claim. It does not catch the existing English-first WOW h3s or the multiline English-only dismiss button, so the current docs/test narrative can report full closure while the page still is not Chinese-first end-to-end.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1548:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1915:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1549:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1916:- IMPORTANT `tests/test_workbench_approval_flow_polish.py:1-15`, `tests/test_workbench_approval_flow_polish.py:61-169`, `src/well_harness/static/workbench.html:111`, `src/well_harness/static/workbench.html:143`, `src/well_harness/static/workbench.html:173`, `src/well_harness/static/workbench.html:219-226`: test coverage matches the six-string approval-center polish, not the stronger page-wide closure claim. It does not catch the existing English-first WOW h3s or the multiline English-only dismiss button, so the current docs/test narrative can report full closure while the page still is not Chinese-first end-to-end.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1553:.planning/phases/E11-workbench-engineer-first-ux/E11-01-BASELINE-PERSONA-REVIEW.md:121:**E11 path**: E11-03 (column rename to verb-based Chinese-first labels) + E11-04 (annotation vocabulary domain-anchoring) + new E11-15 (sweep all UI strings to Chinese-first with English in muted sublabels).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1554:.planning/phases/E11-workbench-engineer-first-ux/E11-01-BASELINE-PERSONA-REVIEW.md:179:| **E11-15** (new) | queued | full UI string sweep — Chinese-first with English muted sublabels |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1556:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:43:   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1558:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-output.md:23:   Suggested mitigation (presentation-friendly): Chinese-first labels on the primary surface; keep English only in muted sublabels.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1563:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-prompt.txt:28:   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1576:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:5:You ran the E11-15d Tier-B review across 3 rounds (R1, R2, R3) and were the persona who flagged the doc-honesty `last English-only surface` / `uniformly Chinese-first` overclaim. Your enumeration of remaining English-only surfaces in E11-15d's R2 review is what E11-15e set out to close.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1577:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:15:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1578:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:16:   - Any forbidden overclaim phrases (`last English-only surface` / `uniformly Chinese-first` / `all English surfaces` / equivalents) that drifted in?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1579:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:18:# Context — E11-15b Chinese-first iter 2 (h1/h2/buttons/caption)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1580:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:51:- **First-glance demo impression**: open `/workbench` cold — does the page now read Chinese-first across header, control buttons, annotation inbox, and approval center? Or is there still residual English-first surface that defeats the goal?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1581:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:53:- **Bilingual delimiter consistency**: every flip uses ` · ` (space-middot-space). Is this consistent with the rest of the codebase's bilingual pattern (e.g., column h2s `Probe & Trace · 探针与追踪`)? Note the column h2s use English-first; the new sweep uses Chinese-first. Is this asymmetry acceptable for demo flow, or does it look inconsistent at a glance?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1582:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:67:- **Reverse direction**: column h2s currently use English-first (`Probe & Trace · 探针与追踪`); could be flipped to Chinese-first in a future sweep for delimiter symmetry.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1584:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:637:+# E11-15b Surface Inventory — Chinese-first h2/button/caption sweep (iter 2)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1585:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:644:+> uniformly Chinese-first while preserving English suffixes for existing
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1586:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:730: E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1587:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:796:+        # h1 main title is bilingualized by E11-15b (Chinese-first); the
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1588:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:809:+"""E11-15b — Chinese-first h2 / button / caption sweep (iter 2).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1589:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:1428:     1	"""E11-15b — Chinese-first h2 / button / caption sweep (iter 2).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1590:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:1726:- `NIT` [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:275): the new sweep is Chinese-first in the hero/review/approval surfaces, but the three main column h2s at lines 275, 295, and 315 are still English-first while the new headings at lines 334 and 380 are Chinese-first. That direction flip is now the most visible remaining polish gap, even though it is correctly treated as deferred scope.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1591:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:1741:- `NIT` [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:275): the new sweep is Chinese-first in the hero/review/approval surfaces, but the three main column h2s at lines 275, 295, and 315 are still English-first while the new headings at lines 334 and 380 are Chinese-first. That direction flip is now the most visible remaining polish gap, even though it is correctly treated as deferred scope.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1593:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:30:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1594:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:32:> **IMPORTANT** — `tests/test_workbench_approval_flow_polish.py:1-15, 61-169`, `workbench.html:111, 143, 173, 219-226`: test coverage matches the six-string approval-center polish, not the stronger page-wide closure claim. It does not catch the existing English-first WOW h3s or the multiline English-only dismiss button, so the current docs/test narrative can report full closure while the page still is not Chinese-first end-to-end.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1595:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:41:- Header banner now states this is "NOT the final Chinese-first sweep" and explicitly references the P2 R1 IMPORTANT.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1596:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:42:- Replaced "Closure summary" section with "Workbench Chinese-first thread progress (NOT closure)" + new explicit "English-only surfaces still remaining" section listing the 4 strings you found (with their existing test-lock locations) + WOW starter h3s + topbar chip labels. Deferred to future E11-15e Tier-A bundle.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1597:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:44:`PERSONA-ROTATION-STATE.md` line 24: rewrote E11-15d entry to remove "Closes the last English-only surface" + "uniformly Chinese-first"; added "P2 R1 IMPORTANT closure" note + same deferred-to-E11-15e list.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1598:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:48:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1599:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:61:- **Did R2 actually close the overclaim?** Re-grep the inventory + rotation-state for `last English-only surface` / `uniformly Chinese-first` outside the leading blockquote and confirm zero hits.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1600:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:63:- **Is the guard test sufficient?** It only catches reintroduction of those 2 specific phrases. Other overclaim phrasings (e.g., "the entire workbench Chinese-first work is done", "no English remains") would slip past. Acceptable trade-off for narrow IMPORTANT closure, OR should the guard be broader?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1602:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:395:     6	> body copy (6 strings). Note: this is NOT the final Chinese-first
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1603:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:399:    10	> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1604:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:467:    78	## Workbench Chinese-first thread progress (NOT closure)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1605:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:469:    80	E11-15d is one slice in a multi-sub-phase Chinese-first thread:
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1610:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:679:   178	    claimed `last English-only surface` and `uniformly Chinese-first`,
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1611:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:696:   195	        "uniformly Chinese-first",
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1612:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:730:    19	E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1613:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:732:    21	E11-15c: Tier-B (4 copy_diff_lines, 4 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit: this sub-phase rewrites existing test contracts in lockstep with HTML changes, so V&V invariant-preservation lens is exactly right). Direct closure of P3's 2 NITs from E11-15b: (a) page eyebrow `控制逻辑工作台` → `工程师工作区` to break duplication with h1; (b) 3 column h2s flipped from English-first to Chinese-first for full-page direction consistency.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1614:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:735:    24	E11-15d: Tier-B (Persona = P2 — Senior FCS Engineer — round-robin successor of E11-10's P1, derived programmatically by next-persona tool. Bilingualizes the Approval Center lane labels: 3 h3s + 2 lane buttons + 1 pending-lane body copy = 6 [REWRITE]; <10 copy_diff → Tier-B. Persona-content fit: P2's lens on visible-copy consistency for the approval-flow surface. P2 R1 IMPORTANT closure: removed earlier overclaim that this sub-phase finished the workbench Chinese-first thread. Surfaces still English-only after E11-15d: `Hide for session` (trust banner dismiss), `Truth Engine — Read Only` (authority headline), `No proposals submitted yet.` (inbox placeholder), `Pending Kogami sign-off` (affordance strong text), and WOW starter card h3s — deferred to follow-up E11-15e.)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1615:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1108:/bin/zsh -lc 'rg -n "last English-only surface|uniformly Chinese-first" .planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/test_workbench_approval_flow_polish.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1616:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1111:tests/test_workbench_approval_flow_polish.py:178:    claimed `last English-only surface` and `uniformly Chinese-first`,
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1617:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1113:tests/test_workbench_approval_flow_polish.py:195:        "uniformly Chinese-first",
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1618:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1115:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1619:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1507:print('uniformly Chinese-first' in text)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1620:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1685:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1621:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1709:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1626:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-prompt.txt:24:- `tests/test_workbench_column_rename.py` — 2 assertion blocks updated (param values + live-route check) for new Chinese-first column h2 strings
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1632:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt:12:Closes the LAST English-only surface in the workbench demo. With this sub-phase, `/workbench` is uniformly Chinese-first; only the backend API remediation message in `demo_server.py:743` stays English (backend contract, locked by `tests/test_lever_snapshot_manual_override_guard.py:151`).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1633:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt:33:- **Visible-copy consistency**: do the 6 new bilingual approval-flow strings work harmoniously with the surrounding E11-15b approval-center surface (`Kogami 提案审批 · Kogami Proposal Triage` h2, `审批中心 · Approval Center` entry button, `审批操作仅限 Kogami · ...` caption)? Does the page now read uniformly as a Chinese-first FCS engineer's approval workflow?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1634:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt:38:- **Closure claim verification**: I claim `/workbench` is now uniformly Chinese-first. Verify by `grep -nE ">[A-Za-z][^<]*</h[1-3]>|>[A-Za-z][^<]*</button>"` on `workbench.html` to confirm no remaining English-only h1/h2/h3/button content. Acceptable exceptions: identifier strings in topbar chips (`Identity`, `Ticket`, `System`, `Feedback Mode`), system option labels (`Thrust Reverser`, etc.) which are domain proper-nouns, and the `eyebrow` decorative labels in the column trio (locked by E11-03 tests).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1635:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt:52:- **Column-trio eyebrows** — locked by E11-03; bilingual h2 already gives Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1636:.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:19:E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1637:.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:21:E11-15c: Tier-B (4 copy_diff_lines, 4 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit: this sub-phase rewrites existing test contracts in lockstep with HTML changes, so V&V invariant-preservation lens is exactly right). Direct closure of P3's 2 NITs from E11-15b: (a) page eyebrow `控制逻辑工作台` → `工程师工作区` to break duplication with h1; (b) 3 column h2s flipped from English-first to Chinese-first for full-page direction consistency.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1638:.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24:E11-15d: Tier-B (Persona = P2 — Senior FCS Engineer — round-robin successor of E11-10's P1, derived programmatically by next-persona tool. Bilingualizes the Approval Center lane labels: 3 h3s + 2 lane buttons + 1 pending-lane body copy = 6 [REWRITE]; <10 copy_diff → Tier-B. Persona-content fit: P2's lens on visible-copy consistency for the approval-flow surface. P2 R1 IMPORTANT closure: removed earlier overclaim that this sub-phase finished the workbench Chinese-first thread. Surfaces still English-only after E11-15d: `Hide for session` (trust banner dismiss), `Truth Engine — Read Only` (authority headline), `No proposals submitted yet.` (inbox placeholder), `Pending Kogami sign-off` (affordance strong text), and WOW starter card h3s — deferred to follow-up E11-15e.)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1639:.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:25:E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1642:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:37:   - The WOW starter cards' h3 changed from English-first to Chinese-first ordering. Does this affect screen-reader announcement order for the `aria-labelledby` linkage (workbench-wow-a-title etc.)? The h3 is the labelled-by target — the rest of the card description still starts with the API endpoint string.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1643:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:40:   - The new `等待 Kogami 签字 · Pending Kogami sign-off` is followed by an existing Chinese-first body span: `你的提案已加入排队，等待 Kogami 处理...`. Does the doubled "等待 Kogami" reading (header + body) feel redundant, or is it OK reinforcement?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1646:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:20:You ran the E11-15d Tier-B review across 3 rounds (R1, R2, R3) and were the persona who flagged the doc-honesty `last English-only surface` / `uniformly Chinese-first` overclaim. Your enumeration of remaining English-only surfaces in E11-15d's R2 review is what E11-15e set out to close.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1647:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:30:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1648:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:31:   - Any forbidden overclaim phrases (`last English-only surface` / `uniformly Chinese-first` / `all English surfaces` / equivalents) that drifted in?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1649:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:140:E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1650:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:142:E11-15c: Tier-B (4 copy_diff_lines, 4 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit: this sub-phase rewrites existing test contracts in lockstep with HTML changes, so V&V invariant-preservation lens is exactly right). Direct closure of P3's 2 NITs from E11-15b: (a) page eyebrow `控制逻辑工作台` → `工程师工作区` to break duplication with h1; (b) 3 column h2s flipped from English-first to Chinese-first for full-page direction consistency.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1651:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:145:E11-15d: Tier-B (Persona = P2 — Senior FCS Engineer — round-robin successor of E11-10's P1, derived programmatically by next-persona tool. Bilingualizes the Approval Center lane labels: 3 h3s + 2 lane buttons + 1 pending-lane body copy = 6 [REWRITE]; <10 copy_diff → Tier-B. Persona-content fit: P2's lens on visible-copy consistency for the approval-flow surface. P2 R1 IMPORTANT closure: removed earlier overclaim that this sub-phase finished the workbench Chinese-first thread. Surfaces still English-only after E11-15d: `Hide for session` (trust banner dismiss), `Truth Engine — Read Only` (authority headline), `No proposals submitted yet.` (inbox placeholder), `Pending Kogami sign-off` (affordance strong text), and WOW starter card h3s — deferred to follow-up E11-15e.)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1652:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:146:E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1653:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:149:# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1659:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:263:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1660:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:279:| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1661:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:292:/bin/zsh -lc 'pwd && git rev-parse --short HEAD && git status --short && rg -n "E11-15e|E11-15d|LogicMVP|persona|surface-inventory|uniformly Chinese-first|last English-only surface" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1667:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:39:- `tests/test_workbench_column_rename.py` — 2 assertion blocks updated (param values + live-route check) for new Chinese-first column h2 strings
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1685:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:632:+| #2: column h2s are still English-first while the rest of the page is Chinese-first | 3 column h2s flipped from `<English> · <中文>` to `<中文> · <English>` for full-page direction consistency |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1686:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:646:+  to expect Chinese-first column h2s (param values + live-route check).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1689:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:678:+1. 3 column h2s positively asserted Chinese-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1692:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:705:+E11-15c: Tier-B (4 copy_diff_lines, 4 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit: this sub-phase rewrites existing test contracts in lockstep with HTML changes, so V&V invariant-preservation lens is exactly right). Direct closure of P3's 2 NITs from E11-15b: (a) page eyebrow `控制逻辑工作台` → `工程师工作区` to break duplication with h1; (b) 3 column h2s flipped from English-first to Chinese-first for full-page direction consistency.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1695:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:728:+"""E11-15c — Chinese-first direction consistency + h1/eyebrow dedup.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1698:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:740:+    while the rest of the page is Chinese-first. E11-15c flips them
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1700:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:789:+# ─── 1. NIT #2: column h2s are now Chinese-first ─────────────────────
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1701:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:802:+    assert chinese_first_h2 in html, f"missing Chinese-first column h2: {chinese_first_h2}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1709:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:939:+        # E11-15c flipped to Chinese-first to match the rest of the page;
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1710:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:949:+    # E11-15c flipped these from English-first to Chinese-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1711:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1022:    64	        # E11-15c flipped to Chinese-first to match the rest of the page;
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1712:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1189:   231	    # E11-15c flipped these from English-first to Chinese-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1713:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1202:     1	"""E11-15 — Chinese-first eyebrow sweep.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1714:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1206:     5	reads Chinese-first at a glance. The 3 column-eyebrows (probe & trace,
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1715:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1209:     8	each already provides Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1717:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1273:    72	    assert eyebrow_html in html, f"missing Chinese-first eyebrow: {eyebrow_html}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1718:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1322:   121	        # h1 main title is bilingualized by E11-15b (Chinese-first); the
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1720:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1550:     1	"""E11-15b — Chinese-first h2 / button / caption sweep (iter 2).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1723:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2236:     1	"""E11-15c — Chinese-first direction consistency + h1/eyebrow dedup.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1726:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2248:    13	    while the rest of the page is Chinese-first. E11-15c flips them
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1728:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2297:    62	# ─── 1. NIT #2: column h2s are now Chinese-first ─────────────────────
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1729:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2310:    75	    assert chinese_first_h2 in html, f"missing Chinese-first column h2: {chinese_first_h2}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1735:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2446:    69	    assert eyebrow_html in html, f"missing Chinese-first eyebrow: {eyebrow_html}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1736:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2495:   118	        # h1 main title is bilingualized by E11-15b (Chinese-first); the
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1755:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:9:1. **Convention adherence — Chinese-first ordering**
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1756:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:10:   - E11-15c established Chinese-first column h2 ordering. Are E11-15e's WOW h3 direction flips (`因果链走读 · Causal Chain` / `1000-trial 可靠性 · Monte Carlo` / `反向诊断 · Reverse Diagnose`) consistent with E11-15c?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1757:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:11:   - Are all 22 REWRITE strings Chinese-first (Chinese before middle dot)?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1758:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:12:   - Is `1000-trial 可靠性 · Monte Carlo` actually "Chinese-first" given the leading "1000-trial" English token? Should it be re-ordered as `可靠性 1000-trial · Monte Carlo` or `1000 次试验可靠性 · Monte Carlo` for stricter convention adherence?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1760:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:32:   - E11-15c flipped column h2s from English-first to Chinese-first. E11-15e flips WOW h3s the same way. But the WOW h3s previously had a different convention — original was English-first. Verify the flip is consistent with the **page-wide direction convention**, not breaking some special case.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1793:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:24:1. **Convention adherence — Chinese-first ordering**
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1794:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:25:   - E11-15c established Chinese-first column h2 ordering. Are E11-15e's WOW h3 direction flips (`因果链走读 · Causal Chain` / `1000-trial 可靠性 · Monte Carlo` / `反向诊断 · Reverse Diagnose`) consistent with E11-15c?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1795:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:26:   - Are all 22 REWRITE strings Chinese-first (Chinese before middle dot)?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1796:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:27:   - Is `1000-trial 可靠性 · Monte Carlo` actually "Chinese-first" given the leading "1000-trial" English token? Should it be re-ordered as `可靠性 1000-trial · Monte Carlo` or `1000 次试验可靠性 · Monte Carlo` for stricter convention adherence?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1798:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:47:   - E11-15c flipped column h2s from English-first to Chinese-first. E11-15e flips WOW h3s the same way. But the WOW h3s previously had a different convention — original was English-first. Verify the flip is consistent with the **page-wide direction convention**, not breaking some special case.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1800:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:200:/bin/zsh -lc 'rg -n "E11-15e|LogicMVP|bilingual|Chinese-first|workbench" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1802:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:363:# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1808:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:477:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1809:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:493:| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1810:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:508:"""E11-15e — Tier-A Chinese-first bundle regression lock.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1812:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:602:        # WOW h3 direction flips (3) — Chinese-first per E11-15c convention
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1815:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-prompt.txt:3:# Context — E11-15b Chinese-first iter 2 (h1/h2/buttons/caption)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1816:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-prompt.txt:36:- **First-glance demo impression**: open `/workbench` cold — does the page now read Chinese-first across header, control buttons, annotation inbox, and approval center? Or is there still residual English-first surface that defeats the goal?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1817:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-prompt.txt:38:- **Bilingual delimiter consistency**: every flip uses ` · ` (space-middot-space). Is this consistent with the rest of the codebase's bilingual pattern (e.g., column h2s `Probe & Trace · 探针与追踪`)? Note the column h2s use English-first; the new sweep uses Chinese-first. Is this asymmetry acceptable for demo flow, or does it look inconsistent at a glance?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1818:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-prompt.txt:52:- **Reverse direction**: column h2s currently use English-first (`Probe & Trace · 探针与追踪`); could be flipped to Chinese-first in a future sweep for delimiter symmetry.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1819:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:15:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1820:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:17:> **IMPORTANT** — `tests/test_workbench_approval_flow_polish.py:1-15, 61-169`, `workbench.html:111, 143, 173, 219-226`: test coverage matches the six-string approval-center polish, not the stronger page-wide closure claim. It does not catch the existing English-first WOW h3s or the multiline English-only dismiss button, so the current docs/test narrative can report full closure while the page still is not Chinese-first end-to-end.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1821:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:26:- Header banner now states this is "NOT the final Chinese-first sweep" and explicitly references the P2 R1 IMPORTANT.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1822:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:27:- Replaced "Closure summary" section with "Workbench Chinese-first thread progress (NOT closure)" + new explicit "English-only surfaces still remaining" section listing the 4 strings you found (with their existing test-lock locations) + WOW starter h3s + topbar chip labels. Deferred to future E11-15e Tier-A bundle.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1823:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:29:`PERSONA-ROTATION-STATE.md` line 24: rewrote E11-15d entry to remove "Closes the last English-only surface" + "uniformly Chinese-first"; added "P2 R1 IMPORTANT closure" note + same deferred-to-E11-15e list.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1824:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:33:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1825:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:46:- **Did R2 actually close the overclaim?** Re-grep the inventory + rotation-state for `last English-only surface` / `uniformly Chinese-first` outside the leading blockquote and confirm zero hits.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1826:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:48:- **Is the guard test sufficient?** It only catches reintroduction of those 2 specific phrases. Other overclaim phrasings (e.g., "the entire workbench Chinese-first work is done", "no English remains") would slip past. Acceptable trade-off for narrow IMPORTANT closure, OR should the guard be broader?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1968:     1	"""E11-15e — Tier-A Chinese-first bundle regression lock.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:2062:    95	        # WOW h3 direction flips (3) — Chinese-first per E11-15c convention

exec
/bin/zsh -lc "git diff --stat main..83d69e4 && echo '---DIFF---' && git diff --unified=0 --word-diff=plain main..83d69e4 -- src/well_harness/static/workbench.html src/well_harness/static/workbench.js tests/test_workbench_e11_15e_chinese_first_bundle.py .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md tests/test_workbench_approval_flow_polish.py .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
 .../E11-15e-SURFACE-INVENTORY.md                   | 141 ++++++++++
 .../PERSONA-ROTATION-STATE.md                      |   1 +
 .../persona-P2-E11-15d-R3-output.md                |  96 +++++++
 .../persona-P2-E11-15d-R3-prompt.txt               |  69 +++++
 src/well_harness/static/workbench.html             |  54 ++--
 src/well_harness/static/workbench.js               |   2 +-
 .../test_workbench_e11_15e_chinese_first_bundle.py | 311 +++++++++++++++++++++
 7 files changed, 646 insertions(+), 28 deletions(-)
---DIFF---
diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md
new file mode 100644
index 0000000..e84b202
--- /dev/null
+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md
@@ -0,0 +1,141 @@
{+# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY+}

{+**Date:** 2026-04-26+}
{+**Status:** in_review (Tier-A, ≥15 REWRITE rows → 5-persona dispatch)+}
{+**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`+}
{+**Scope:** Bilingualize the user-visible English-only surfaces on `/workbench`+}
{+that P2 enumerated during the E11-15d Tier-B review (see+}
{+`tests/test_workbench_approval_flow_polish.py:189-194`).+}

{+---+}

{+## 1. Tier classification+}

{+Per the constitution, Tier = **Tier-A** iff+}
{+`copy_diff_lines ≥ 10 AND (REWRITE + DELETE) count ≥ 3`.+}

{+| Metric | Count |+}
{+|--------|------:|+}
{+| copy_diff_lines (workbench.html + workbench.js)        | ~38 |+}
{+| REWRITE rows (display strings rewritten in place)      | **22** |+}
{+| DELETE rows (English-only string removed without bilingual replacement) | 0 |+}
{+| ADD rows (new strings introduced for the first time)   | 0 |+}

{+**Verdict: Tier-A.** Dispatch round-robin successor of E11-15d's P2 → **P3**, plus+}
{+P1, P2, P4, P5 per Tier-A 5-persona requirement.+}

{+---+}

{+## 2. Surface table (REWRITE = 22)+}

{+Pattern across all rows: `<中文> · <English>`. The English suffix is preserved+}
{+verbatim so prior-sub-phase substring locks (`assert <english> in html`) keep+}
{+passing without contract churn.+}

{+| # | Surface | File:Line | Old (English-only) | New (bilingual) |+}
{+|---|---------|-----------|---------------------|-----------------|+}
{+| 1 | Identity chip label | workbench.html:26 | `<span>Identity</span>` | `<span>身份 · Identity</span>` |+}
{+| 2 | Ticket chip label | workbench.html:30 | `<span>Ticket</span>` | `<span>工单 · Ticket</span>` |+}
{+| 3 | Feedback Mode chip label | workbench.html:41 | `<span>Feedback Mode</span>` | `<span>反馈模式 · Feedback Mode</span>` |+}
{+| 4 | Manual (advisory) chip text (HTML) | workbench.html:42 | `<strong>Manual (advisory)</strong>` | `<strong>手动（仅参考）· Manual (advisory)</strong>` |+}
{+| 5 | Manual (advisory) chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Manual (advisory)"` literal | `"手动（仅参考）· Manual (advisory)"` |+}
{+| 6 | Truth Engine chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Truth Engine"` literal | `"真值引擎 · Truth Engine"` |+}
{+| 7 | System chip label | workbench.html:46 | `<span>System</span>` | `<span>系统 · System</span>` |+}
{+| 8 | WOW h3 (wow_a) — direction flip | workbench.html:111 | `Causal Chain · 因果链走读` | `因果链走读 · Causal Chain` |+}
{+| 9 | WOW h3 (wow_b) — direction flip | workbench.html:143 | `Monte Carlo · 1000-trial 可靠性` | `1000-trial 可靠性 · Monte Carlo` |+}
{+| 10 | WOW h3 (wow_c) — direction flip | workbench.html:173 | `Reverse Diagnose · 反向诊断` | `反向诊断 · Reverse Diagnose` |+}
{+| 11 | State-of-world label · sha | workbench.html:65 | `truth-engine SHA` | `真值引擎 SHA · truth-engine SHA` |+}
{+| 12 | State-of-world label · e2e | workbench.html:71 | `recent e2e` | `最近 e2e · recent e2e` |+}
{+| 13 | State-of-world label · adversarial | workbench.html:77 | `adversarial` | `对抗样本 · adversarial` |+}
{+| 14 | State-of-world label · open issues | workbench.html:83 | `open issues` | `未关闭问题 · open issues` |+}
{+| 15 | State-of-world advisory flag | workbench.html:87 | `advisory · not a live truth-engine reading` | `仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading` |+}
{+| 16 | Trust banner scope `<em>` | workbench.html:209-211 | `<em>What "manual feedback" means here:</em> any value...` | `<em>这里"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入...` |+}
{+| 17 | Trust banner advisory `<strong>` | workbench.html:213 | `<strong>That mode is advisory.</strong>` | `<strong>该模式仅作参考 · That mode is advisory.</strong>` |+}
{+| 18 | Trust banner truth-engine `<span>` | workbench.html:215-217 | `Truth engine readings (logic gates L1–L4 ...)` | `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings ...` |+}
{+| 19 | Trust banner dismiss button | workbench.html:225 | `Hide for session` | `隐藏（本次会话）· Hide for session` |+}
{+| 20 | Authority banner headline | workbench.html:248 | `Truth Engine — Read Only` | `真值引擎 · 只读 · Truth Engine — Read Only` |+}
{+| 21 | Pre-hydration boot status (control panel) | workbench.html:278 | `Waiting for probe & trace panel boot.` | `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` |+}
{+| 22 | Pre-hydration boot status (document panel) | workbench.html:298 | `Waiting for annotate & propose panel boot.` | `等待 annotate & propose 面板启动 · Waiting for annotate & propose panel boot.` |+}
{+| 23 | Pre-hydration boot status (circuit panel) | workbench.html:318 | `Waiting for hand off & track panel boot.` | `等待 hand off & track 面板启动 · Waiting for hand off & track panel boot.` |+}
{+| 24 | Reference packet intro `<p>` | workbench.html:301 | `Reference packet, clarification notes...` | `参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, ...` |+}
{+| 25 | Annotation inbox empty state | workbench.html:337 | `<li>No proposals submitted yet.</li>` | `<li>暂无已提交提案 · No proposals submitted yet.</li>` |+}
{+| 26 | Pending sign-off `<strong>` | workbench.html:363 | `<strong>Pending Kogami sign-off</strong>` | `<strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>` |+}

{+(22 rows after dedup of #5/#6 with their HTML siblings; the table uses 26 row IDs+}
{+for line-of-evidence but treats #4+#5 and #11-#14+#15 as single `surface diff`+}
{+counts in the metric table above.)+}

{+---+}

{+## 3. Out of scope (explicitly deferred — surface-honesty closure)+}

{+E11-15e is **NOT** "the last English-only surface" on `/workbench`. The+}
{+following surfaces remain English-only and are **deferred to future sub-phases+}
{+or constitutional decisions**, not silently included:+}

{+| Deferred surface | Why deferred | File:Line |+}
{+|------------------|--------------|-----------|+}
{+| `<option>` system values (`Thrust Reverser`, `Landing Gear`, `Bleed Air Valve`, `C919 E-TRAS`) | Domain proper nouns coupled to value-attribute IDs and the multi-system adapter dispatch in `tests/test_p19_api_multisystem.py`. Bilingualizing the option text would require coordinated changes to value-id parsing, locale-mapping, and the adapter contract. | workbench.html:48-51 |+}
{+| Post-hydration JS boot status strings (`Probe & Trace ready. Scenario actions are staged for the next bundle.` × 3) | Locked by `tests/test_workbench_column_rename.py:170-172`; would require workbench.js bilingualization with its own lockstep test contract. **Note:** This is the string users actually see for most of session — the "Waiting for ... panel boot." strings E11-15e bilingualizes are pre-hydration only. Re-tier as Tier-A for a follow-up sub-phase. | workbench.js boot fns |+}
{+| `<pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>` | Visual phase-arrow diagram, not English copy. Would require a Chinese arrow notation decision (e.g. `承接 → 澄清 → 回放 → 诊断 → 知识`); deferred to UX/copy decision. | workbench.html:302 |+}
{+| `data-wow-id="wow_a"` attribute strings + `data-wow-action="run"` | Internal data-* attributes, not user-visible — out of bilingualization scope by design. | workbench.html:104-194 |+}
{+| `wow_a/b/c` tag spans (`<span class="workbench-wow-tag">wow_a</span>`) | Card identifier sigil, not display copy; these literally name the API endpoint group. | workbench.html:110/142/172 |+}
{+| Eyebrow `probe & trace` / `annotate & propose` / `hand off & track` (lowercase column eyebrows) | These are paired with the bilingual `<h2>` titles E11-15c shipped (e.g. `<h2>探针与追踪 · Probe & Trace</h2>`). Eyebrows are intentionally English-only for the column-key tag pattern; if revisited, would need its own constitutional pass. | workbench.html:274/294/314 |+}
{+| `WB-E06-SHELL` ticket id, `Kogami / Engineer` identity | Identifiers/proper nouns, not display copy. | workbench.html:27/31 |+}

{+**Surface-honesty pledge:** This sub-phase closes 22 surfaces. It does NOT close+}
{+"all" or "the last". The deferred list above is **non-exhaustive** — if a+}
{+reviewer finds another English-only user-visible surface not listed here that is+}
{+neither REWRITE in this slice nor in the deferred table, that finding is+}
{+**legitimate** and a CHANGES_REQUIRED is appropriate.+}

{+---+}

{+## 4. Truth-engine red line+}

{+Display-copy edits only. `controller.py` / `runner.py` / `models.py` /+}
{+`src/well_harness/adapters/` / `demo_server.py` are **untouched**. Lockstep+}
{+guard at `tests/test_workbench_e11_15e_chinese_first_bundle.py::+}
{+test_e11_15e_does_not_touch_truth_engine_backend` scans backend files for any+}
{+of the 23 Chinese display strings introduced here.+}

{+---+}

{+## 5. Lockstep test impact+}

{+| Existing test file | Impact | Reason |+}
{+|--------------------|--------|--------|+}
{+| `test_workbench_trust_affordance.py` | ✅ no change | All 5 substring locks (`Manual (advisory)`, `Truth engine readings`, `Hide for session`, `What "manual feedback" means here`, `That mode is advisory.`) are preserved as English suffixes. |+}
{+| `test_workbench_authority_banner.py` | ✅ no change | `Truth Engine — Read Only` preserved as suffix. |+}
{+| `test_workbench_role_affordance.py` | ✅ no change | `Pending Kogami sign-off` preserved as suffix. |+}
{+| `test_workbench_column_rename.py` | ✅ no change | Pre-hydration `Waiting for ... panel boot.` substrings preserved as suffixes; post-hydration JS strings unchanged (out of scope). |+}
{+| `test_workbench_state_of_world_bar.py` | ✅ no change | `advisory · not a live truth-engine reading` preserved as suffix. |+}
{+| `test_workbench_chinese_direction_consistency.py` | ✅ no change | E11-15c column h2 invariant unaffected (no h2 changes). |+}
{+| `test_workbench_chinese_h2_button_sweep.py` | ✅ no change | h2/button sweep targets are already-bilingual surfaces. |+}
{+| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |+}
{+| `test_workbench_e11_15e_chinese_first_bundle.py` (new) | ✅ added | 67 tests — positive bilingual locks, stale-English negative guards, English-suffix preservation locks, structural anchors, JS lockstep, live-served route, truth-engine red-line guard. |+}

{+Full suite verification: **1221 passed, 0 regressions** (pre-PR baseline 1154).+}

{+---+}

{+## 6. Persona dispatch plan+}

{+Tier-A → 5-persona round-robin. E11-15d closed with P2 → successor for E11-15e+}
{+**lead** is **P3**.+}

{+| Persona | Lens |+}
{+|---------|------|+}
{+| P1 | Engineer-task-flow regression |+}
{+| P2 | Surface-inventory honesty + closure-claim guards |+}
{+| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |+}
{+| P4 | Lockstep test contract preservation (no churn on existing locks) |+}
{+| P5 | Truth-engine red-line + JS-HTML lockstep |+}

{+**Codex degradation contingency:** if all 5 codex accounts are+}
{+secondary-window-throttled or token-refresh-failed (as in E11-15d R3), apply+}
{+**Executor 即 Gate (v3.2 治理折叠)** per the project memory rule:+}
{+Claude Code Opus 4.7 self-signs the Tier-A gate, transparently documenting the+}
{+fallback in PR body + `dev_handoff.md` + this inventory's persona-rotation+}
{+entry. Self-signing requires the standard 1221-test green + repo-honesty self-+}
{+review (this inventory + Section 3 surface-honesty pledge satisfy that bar).+}
diff --git a/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md b/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
index 725262d..6c7fc37 100644
--- a/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
+++ b/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
@@ -24,0 +25 @@ E11-15d: Tier-B (Persona = P2 — Senior FCS Engineer — round-robin successor
{+E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.+}
diff --git a/src/well_harness/static/workbench.html b/src/well_harness/static/workbench.html
index cbc80a4..157518a 100644
--- a/src/well_harness/static/workbench.html
+++ b/src/well_harness/static/workbench.html
@@ -26 +26 @@
          [-<span>Identity</span>-]{+<span>身份 · Identity</span>+}
@@ -30 +30 @@
          [-<span>Ticket</span>-]{+<span>工单 · Ticket</span>+}
@@ -41,2 +41,2 @@
          [-<span>Feedback-]{+<span>反馈模式 · Feedback+} Mode</span>
          [-<strong>Manual-]{+<strong>手动（仅参考）· Manual+} (advisory)</strong>
@@ -46 +46 @@
          [-<span>System</span>-]{+<span>系统 · System</span>+}
@@ -65 +65 @@
          <span [-class="workbench-sow-label">truth-engine-]{+class="workbench-sow-label">真值引擎 SHA · truth-engine+} SHA</span>
@@ -71 +71 @@
          <span [-class="workbench-sow-label">recent-]{+class="workbench-sow-label">最近 e2e · recent+} e2e</span>
@@ -77 +77 @@
          <span [-class="workbench-sow-label">adversarial</span>-]{+class="workbench-sow-label">对抗样本 · adversarial</span>+}
@@ -83 +83 @@
          <span [-class="workbench-sow-label">open-]{+class="workbench-sow-label">未关闭问题 · open+} issues</span>
@@ -87 +87 @@
          {+仅参考 · 非真值引擎实时读数 ·+} advisory · not a live truth-engine reading
@@ -111 +111 @@
              <h3 [-id="workbench-wow-a-title">Causal Chain-]{+id="workbench-wow-a-title">因果链走读+} · [-因果链走读</h3>-]{+Causal Chain</h3>+}
@@ -143 +143 @@
              <h3 [-id="workbench-wow-b-title">Monte Carlo-]{+id="workbench-wow-b-title">1000-trial 可靠性+} · [-1000-trial 可靠性</h3>-]{+Monte Carlo</h3>+}
@@ -173 +173 @@
              <h3 [-id="workbench-wow-c-title">Reverse Diagnose-]{+id="workbench-wow-c-title">反向诊断+} · [-反向诊断</h3>-]{+Reverse Diagnose</h3>+}
@@ -209,3 +209,3 @@
            [-<em>What-]{+<em>这里"手动反馈"的含义 · What+} "manual feedback" means here:</em> [-any-]{+你在工作台中手动键入用来覆盖某个观测读数的任何值——例如在运行一个场景前编辑快照输入字段+}
{+            (any+} value you type into the workbench to override an observed reading — for example, editing a snapshot input field before running a [-scenario.-]
[-            Passive-]{+scenario).+}
{+            被动读取、回放与审计链导航不算 manual feedback (Passive+} reads, replays, and audit-chain navigation do NOT count as manual [-feedback.-]{+feedback).+}
@@ -213 +213 @@
          [-<strong>That-]{+<strong>该模式仅作参考 · That+} mode is advisory.</strong>
@@ -215,2 +215,2 @@
            {+真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 ·+} Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative.
            {+你的手动反馈会被记录用于 diff / review，但不改写真值 ·+} Your manual feedback is recorded for diff/review but does not change source-of-truth values.
@@ -225 +225 @@
          {+隐藏（本次会话）·+} Hide for session
@@ -248 +248 @@
          {+真值引擎 · 只读 ·+} Truth Engine — Read Only
@@ -278 +278 @@
            {+等待 probe &amp; trace 面板启动 ·+} Waiting for probe &amp; trace panel boot.
@@ -298 +298 @@
            {+等待 annotate &amp; propose 面板启动 ·+} Waiting for annotate &amp; propose panel boot.
@@ -301 +301 @@
            [-<p>Reference-]{+<p>参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference+} packet, clarification notes, and future text-range annotations will land here.</p>
@@ -318 +318 @@
            {+等待 hand off &amp; track 面板启动 ·+} Waiting for hand off &amp; track panel boot.
@@ -337 +337 @@
          [-<li>No-]{+<li>暂无已提交提案 · No+} proposals submitted yet.</li>
@@ -363 +363 @@
          [-<strong>Pending-]{+<strong>等待 Kogami 签字 · Pending+} Kogami sign-off</strong>
diff --git a/src/well_harness/static/workbench.js b/src/well_harness/static/workbench.js
index 375e6c9..33a247a 100644
--- a/src/well_harness/static/workbench.js
+++ b/src/well_harness/static/workbench.js
@@ -3788 +3788 @@ function setFeedbackMode(mode) {
      label.textContent = mode === "truth_engine" ? [-"Truth-]{+"真值引擎 · Truth+} Engine" : [-"Manual-]{+"手动（仅参考）· Manual+} (advisory)";
diff --git a/tests/test_workbench_e11_15e_chinese_first_bundle.py b/tests/test_workbench_e11_15e_chinese_first_bundle.py
new file mode 100644
index 0000000..46ef2ee
--- /dev/null
+++ b/tests/test_workbench_e11_15e_chinese_first_bundle.py
@@ -0,0 +1,311 @@
{+"""E11-15e — Tier-A Chinese-first bundle regression lock.+}

{+Bilingualizes 17 user-visible English-only surfaces enumerated by P2+}
{+during the E11-15d review (see test_workbench_approval_flow_polish.py+}
{+docstring Section 7 + .planning/phases/E11-workbench-engineer-first-ux/+}
{+E11-15d-SURFACE-INVENTORY.md):+}

{+  Topbar chips (5):       身份/工单/反馈模式/系统 + Manual (advisory) chip+}
{+  WOW h3 direction (3):   Causal Chain / Monte Carlo / Reverse Diagnose+}
{+  State-of-world (5):     truth-engine SHA / recent e2e / adversarial /+}
{+                          open issues / advisory flag+}
{+  Trust banner body (3):  scope <em>, advisory <strong>, truth-engine <span>+}
{+  Authority banner (1):   Truth Engine — Read Only headline+}
{+  Trust dismiss (1):      Hide for session button+}
{+  Boot placeholders (3):  pre-hydration "Waiting for ... panel boot."+}
{+  Reference packet (1):   Annotate column intro <p>+}
{+  Inbox empty (1):        No proposals submitted yet.+}
{+  Pending sign-off (1):   Pending Kogami sign-off+}

{+Pattern: `<中文> · <English>` everywhere; English suffix is preserved+}
{+verbatim so all prior `assert <english> in html` substring locks across+}
{+test_workbench_trust_affordance, test_workbench_authority_banner,+}
{+test_workbench_role_affordance, test_workbench_column_rename, and+}
{+test_workbench_state_of_world_bar continue to pass without contract+}
{+churn.+}

{+Out of scope (deferred to a future Tier-A or constitutional decision):+}
{+  - <option> system values (`Thrust Reverser`, `Landing Gear`, etc.) —+}
{+    domain proper nouns coupled to value-attribute IDs and to the+}
{+    multi-system adapter dispatch in tests/test_p19_api_multisystem.py.+}
{+  - Post-hydration JS boot status strings (`Probe & Trace ready. ...`)+}
{+    locked by tests/test_workbench_column_rename.py:170-172 — those are+}
{+    a separate JS-side bilingualization with their own lockstep contract.+}
{+  - <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge+}
{+    </pre> flow diagram — visual phase-arrow, not English copy.+}
{+  - Workbench-bundle / approval-center / annotation-toolbar surfaces+}
{+    that were already bilingualized in earlier sub-phases.+}

{+Test-tier rationale: ≥15 REWRITE strings → Tier-A per the constitution.+}
{+"""+}

{+from __future__ import annotations+}

{+import http.client+}
{+import threading+}
{+from http.server import ThreadingHTTPServer+}
{+from pathlib import Path+}

{+import pytest+}

{+from well_harness.demo_server import DemoRequestHandler+}


{+REPO_ROOT = Path(__file__).resolve().parents[1]+}
{+STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"+}


{+def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:+}
{+    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)+}
{+    thread = threading.Thread(target=server.serve_forever, daemon=True)+}
{+    thread.start()+}
{+    return server, thread+}


{+def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:+}
{+    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)+}
{+    connection.request("GET", path)+}
{+    response = connection.getresponse()+}
{+    return response.status, response.read().decode("utf-8")+}


{+@pytest.fixture+}
{+def server():+}
{+    s, t = _start_demo_server()+}
{+    try:+}
{+        yield s+}
{+    finally:+}
{+        s.shutdown()+}
{+        s.server_close()+}
{+        t.join(timeout=2)+}


{+# ─── 1. Bilingualized strings POSITIVELY locked ──────────────────────+}


{+@pytest.mark.parametrize(+}
{+    "bilingual",+}
{+    [+}
{+        # Topbar chip labels (5)+}
{+        "<span>身份 · Identity</span>",+}
{+        "<span>工单 · Ticket</span>",+}
{+        "<span>反馈模式 · Feedback Mode</span>",+}
{+        "<span>系统 · System</span>",+}
{+        "<strong>手动（仅参考）· Manual (advisory)</strong>",+}
{+        # WOW h3 direction flips (3) — Chinese-first per E11-15c convention+}
{+        '<h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>',+}
{+        '<h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>',+}
{+        '<h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>',+}
{+        # State-of-world labels (4) + advisory flag (1)+}
{+        "真值引擎 SHA · truth-engine SHA",+}
{+        "最近 e2e · recent e2e",+}
{+        "对抗样本 · adversarial",+}
{+        "未关闭问题 · open issues",+}
{+        "仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading",+}
{+        # Trust banner body (3)+}
{+        '这里"手动反馈"的含义 · What "manual feedback" means here:',+}
{+        "该模式仅作参考 · That mode is advisory.",+}
{+        "真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings",+}
{+        # Trust banner dismiss (1)+}
{+        "隐藏（本次会话）· Hide for session",+}
{+        # Authority banner headline (1)+}
{+        "真值引擎 · 只读 · Truth Engine — Read Only",+}
{+        # Pre-hydration boot placeholders (3)+}
{+        "等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.",+}
{+        "等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.",+}
{+        "等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot.",+}
{+        # Reference-packet intro (1)+}
{+        "参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes",+}
{+        # Inbox empty state (1)+}
{+        "暂无已提交提案 · No proposals submitted yet.",+}
{+        # Pending sign-off (1)+}
{+        "等待 Kogami 签字 · Pending Kogami sign-off",+}
{+    ],+}
{+)+}
{+def test_workbench_html_carries_bilingual_e11_15e_string(bilingual: str) -> None:+}
{+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")+}
{+    assert bilingual in html, f"missing E11-15e bilingual string: {bilingual}"+}


{+# ─── 2. Stale English-only surfaces are gone ─────────────────────────+}


{+@pytest.mark.parametrize(+}
{+    "stale",+}
{+    [+}
{+        # Bare topbar chip labels (no Chinese prefix) — must be replaced+}
{+        "<span>Identity</span>",+}
{+        "<span>Ticket</span>",+}
{+        "<span>Feedback Mode</span>",+}
{+        "<span>System</span>",+}
{+        "<strong>Manual (advisory)</strong>",+}
{+        # WOW h3 stale English-first ordering (E11-15c convention)+}
{+        '<h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>',+}
{+        '<h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>',+}
{+        '<h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>',+}
{+        # Bare state-of-world labels (no Chinese prefix)+}
{+        ">truth-engine SHA<",+}
{+        ">recent e2e<",+}
{+        ">adversarial<",+}
{+        ">open issues<",+}
{+        # Bare trust-banner body lines — these are now sentence-internal+}
{+        # so we look for the line-leading position they used to hold.+}
{+        "<em>What \"manual feedback\" means here:</em>",+}
{+        "<strong>That mode is advisory.</strong>",+}
{+        # Bare button + headline + boot placeholders+}
{+        ">\n          Hide for session\n        <",+}
{+        ">\n          Truth Engine — Read Only\n        <",+}
{+        ">\n            Waiting for probe &amp; trace panel boot.\n          <",+}
{+        ">\n            Waiting for annotate &amp; propose panel boot.\n          <",+}
{+        ">\n            Waiting for hand off &amp; track panel boot.\n          <",+}
{+        # Bare inbox + pending sign-off+}
{+        "<li>No proposals submitted yet.</li>",+}
{+        "<strong>Pending Kogami sign-off</strong>",+}
{+    ],+}
{+)+}
{+def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:+}
{+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")+}
{+    assert stale not in html, f"stale English-only surface still present: {stale}"+}


{+# ─── 3. English suffixes preserved (substring locks unchanged) ───────+}


{+@pytest.mark.parametrize(+}
{+    "preserved_english_suffix",+}
{+    [+}
{+        # Anchors required by trust_affordance.py+}
{+        "Manual (advisory)",+}
{+        "Truth engine readings",+}
{+        "Hide for session",+}
{+        'What "manual feedback" means here',+}
{+        "That mode is advisory.",+}
{+        # Anchor required by authority_banner.py+}
{+        "Truth Engine — Read Only",+}
{+        # Anchor required by role_affordance.py+}
{+        "Pending Kogami sign-off",+}
{+        # Anchor required by state_of_world_bar.py+}
{+        "advisory · not a live truth-engine reading",+}
{+        # Anchors required by column_rename.py:118-120 (pre-hydration)+}
{+        "Waiting for probe &amp; trace panel boot.",+}
{+        "Waiting for annotate &amp; propose panel boot.",+}
{+        "Waiting for hand off &amp; track panel boot.",+}
{+    ],+}
{+)+}
{+def test_e11_15e_preserves_english_suffix_locks(preserved_english_suffix: str) -> None:+}
{+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")+}
{+    assert preserved_english_suffix in html, (+}
{+        f"E11-15e broke English-suffix substring lock: {preserved_english_suffix}"+}
{+    )+}


{+# ─── 4. Structural anchors preserved ─────────────────────────────────+}


{+@pytest.mark.parametrize(+}
{+    "anchor",+}
{+    [+}
{+        'id="workbench-feedback-mode"',+}
{+        'id="workbench-trust-banner"',+}
{+        'id="workbench-authority-banner"',+}
{+        'id="workbench-pending-signoff-affordance"',+}
{+        'id="workbench-state-of-world-bar"',+}
{+        'id="workbench-wow-starters"',+}
{+        'data-trust-banner-dismiss',+}
{+        'data-feedback-mode="manual_feedback_override"',+}
{+    ],+}
{+)+}
{+def test_e11_15e_preserves_structural_anchors(anchor: str) -> None:+}
{+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")+}
{+    assert anchor in html, f"E11-15e broke structural anchor: {anchor}"+}


{+# ─── 5. workbench.js feedback-mode chip stays in lockstep with HTML ──+}


{+def test_workbench_js_feedback_mode_label_is_bilingualized() -> None:+}
{+    """workbench.js:3788 dynamically rewrites the chip <strong> on mode+}
{+    switch. If the JS literal stays English-only, the very first mode+}
{+    flip would silently revert the static HTML's bilingual chip back to+}
{+    `Manual (advisory)` / `Truth Engine`. Lock both branches."""+}
{+    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")+}
{+    assert '"真值引擎 · Truth Engine"' in js, (+}
{+        "JS feedback-mode `truth_engine` branch must use bilingual label"+}
{+    )+}
{+    assert '"手动（仅参考）· Manual (advisory)"' in js, (+}
{+        "JS feedback-mode `manual_feedback_override` branch must use bilingual label"+}
{+    )+}
{+    # Stale English-only literals must not coexist (would imply duplicate+}
{+    # write-paths or stale residue).+}
{+    assert '"Truth Engine"' not in js, (+}
{+        'stale English-only `"Truth Engine"` literal still in workbench.js'+}
{+    )+}
{+    assert '"Manual (advisory)"' not in js, (+}
{+        'stale English-only `"Manual (advisory)"` literal still in workbench.js'+}
{+    )+}


{+# ─── 6. Live-served route reflects E11-15e end-to-end ────────────────+}


{+def test_workbench_route_serves_e11_15e_bundle(server) -> None:+}
{+    status, html = _get(server, "/workbench")+}
{+    assert status == 200+}
{+    # Spot-check one string from each surface category.+}
{+    assert "身份 · Identity" in html+}
{+    assert "因果链走读 · Causal Chain" in html+}
{+    assert "真值引擎 SHA · truth-engine SHA" in html+}
{+    assert "该模式仅作参考 · That mode is advisory." in html+}
{+    assert "隐藏（本次会话）· Hide for session" in html+}
{+    assert "真值引擎 · 只读 · Truth Engine — Read Only" in html+}
{+    assert "等待 probe &amp; trace 面板启动" in html+}
{+    assert "暂无已提交提案 · No proposals submitted yet." in html+}
{+    assert "等待 Kogami 签字 · Pending Kogami sign-off" in html+}


{+# ─── 7. Truth-engine red line — backend untouched ────────────────────+}


{+def test_e11_15e_does_not_touch_truth_engine_backend() -> None:+}
{+    """E11-15e only edits static HTML/JS display copy. It must NOT leak+}
{+    into controller.py / runner.py / models.py / adapters / demo_server+}
{+    (truth-engine red line — see .planning/constitution.md)."""+}
{+    repo_root = Path(__file__).resolve().parents[1]+}
{+    backend_paths = [+}
{+        repo_root / "src" / "well_harness" / "controller.py",+}
{+        repo_root / "src" / "well_harness" / "runner.py",+}
{+        repo_root / "src" / "well_harness" / "models.py",+}
{+        repo_root / "src" / "well_harness" / "demo_server.py",+}
{+    ]+}
{+    e11_15e_chinese = [+}
{+        "身份 · Identity",+}
{+        "工单 · Ticket",+}
{+        "反馈模式 · Feedback Mode",+}
{+        "系统 · System",+}
{+        "手动（仅参考）",+}
{+        "因果链走读",+}
{+        "1000-trial 可靠性",+}
{+        "反向诊断 · Reverse Diagnose",+}
{+        "真值引擎 SHA",+}
{+        "最近 e2e",+}
{+        "对抗样本",+}
{+        "未关闭问题",+}
{+        "仅参考 · 非真值引擎实时读数",+}
{+        '这里"手动反馈"的含义',+}
{+        "该模式仅作参考",+}
{+        "隐藏（本次会话）",+}
{+        "真值引擎 · 只读",+}
{+        "等待 probe",+}
{+        "等待 annotate",+}
{+        "等待 hand off",+}
{+        "参考资料、澄清说明",+}
{+        "暂无已提交提案",+}
{+        "等待 Kogami 签字",+}
{+    ]+}
{+    for backend in backend_paths:+}
{+        text = backend.read_text(encoding="utf-8")+}
{+        for phrase in e11_15e_chinese:+}
{+            assert phrase not in text, (+}
{+                f"E11-15e display copy {phrase!r} unexpectedly leaked into "+}
{+                f"backend file {backend.name} — truth-engine red-line breach"+}
{+            )+}

codex
`gsd-code-review` 的本地 skill 文件在当前路径下不可读，我继续按同一 findings-first 规则做原生审计。下一步把 P2 的旧清单、现有 22-row inventory、真实 `/workbench` HTML 三方对齐，确认是否有漏项。
Running a read-only P2 audit across closure coverage, overclaim guards, deferred completeness, tier math, and persona succession.
  → Cross-reference E11-15d P2 prior findings against E11-15e Section 2/3 and current diff
  • Audit overclaim language in inventory/tests and compare against E11-15d guard semantics
  • Walk current /workbench surfaces for missing English-only items outside rewrite/deferred lists
  • Recompute Tier-A metrics and persona successor from repo state/tooling
  • Write P2 verdict with severity-tagged findings and precise file:line refs
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '1,420p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	<!doctype html>
     2	<html lang="zh-CN">
     3	  <head>
     4	    <meta charset="utf-8">
     5	    <meta name="viewport" content="width=device-width, initial-scale=1">
     6	    <title>Control Logic Workbench</title>
     7	    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
     8	    <link rel="apple-touch-icon" href="/apple-touch-icon.svg">
     9	    <link rel="manifest" href="/manifest.json">
    10	    <link rel="stylesheet" href="/demo.css">
    11	    <link rel="stylesheet" href="/workbench.css">
    12	  </head>
    13	  <body data-view="beginner">
    14	    <main class="shell workbench-shell">
    15	      <section id="workbench-topbar" class="workbench-collab-topbar" aria-label="Workbench identity and routing">
    16	        <div class="workbench-collab-brand">
    17	          <p class="eyebrow">工程师工作区</p>
    18	          <h1>控制逻辑工作台 · Control Logic Workbench</h1>
    19	        </div>
    20	        <div
    21	          id="workbench-identity"
    22	          class="workbench-collab-chip"
    23	          data-role="ENGINEER"
    24	          data-identity-name="Kogami"
    25	        >
    26	          <span>身份 · Identity</span>
    27	          <strong>Kogami / Engineer</strong>
    28	        </div>
    29	        <div id="workbench-ticket" class="workbench-collab-chip" data-ticket="WB-E06-SHELL">
    30	          <span>工单 · Ticket</span>
    31	          <strong>WB-E06-SHELL</strong>
    32	        </div>
    33	        <div
    34	          id="workbench-feedback-mode"
    35	          class="workbench-collab-chip workbench-feedback-mode-chip"
    36	          data-feedback-mode="manual_feedback_override"
    37	          data-mode-authority="advisory"
    38	          aria-live="polite"
    39	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
    40	        >
    41	          <span>反馈模式 · Feedback Mode</span>
    42	          <strong>手动（仅参考）· Manual (advisory)</strong>
    43	          <span class="workbench-feedback-mode-dot" aria-hidden="true"></span>
    44	        </div>
    45	        <label class="workbench-collab-system" for="workbench-system-select">
    46	          <span>系统 · System</span>
    47	          <select id="workbench-system-select">
    48	            <option value="thrust-reverser">Thrust Reverser</option>
    49	            <option value="landing-gear">Landing Gear</option>
    50	            <option value="bleed-air-valve">Bleed Air Valve</option>
    51	            <option value="c919-etras">C919 E-TRAS</option>
    52	          </select>
    53	        </label>
    54	      </section>
    55	
    56	      <section
    57	        id="workbench-state-of-world-bar"
    58	        class="workbench-state-of-world-bar"
    59	        aria-label="State-of-the-world status bar (advisory)"
    60	        data-status-kind="advisory"
    61	      >
    62	        <span class="workbench-sow-eyebrow">当前现状</span>
    63	        <span class="workbench-sow-field" data-sow-field="truth_engine_sha"
    64	              title="git rev-parse --short HEAD">
    65	          <span class="workbench-sow-label">真值引擎 SHA · truth-engine SHA</span>
    66	          <span class="workbench-sow-value" data-sow-value="truth_engine_sha">…</span>
    67	        </span>
    68	        <span class="workbench-sow-sep" aria-hidden="true">·</span>
    69	        <span class="workbench-sow-field" data-sow-field="recent_e2e"
    70	              title="docs/coordination/qa_report.md (most recent test run)">
    71	          <span class="workbench-sow-label">最近 e2e · recent e2e</span>
    72	          <span class="workbench-sow-value" data-sow-value="recent_e2e_label">…</span>
    73	        </span>
    74	        <span class="workbench-sow-sep" aria-hidden="true">·</span>
    75	        <span class="workbench-sow-field" data-sow-field="adversarial"
    76	              title="docs/coordination/qa_report.md (shared validation)">
    77	          <span class="workbench-sow-label">对抗样本 · adversarial</span>
    78	          <span class="workbench-sow-value" data-sow-value="adversarial_label">…</span>
    79	        </span>
    80	        <span class="workbench-sow-sep" aria-hidden="true">·</span>
    81	        <span class="workbench-sow-field" data-sow-field="known_issues"
    82	              title="docs/known-issues/ file count">
    83	          <span class="workbench-sow-label">未关闭问题 · open issues</span>
    84	          <span class="workbench-sow-value" data-sow-value="open_known_issues_count">…</span>
    85	        </span>
    86	        <span class="workbench-sow-flag" aria-hidden="false">
    87	          仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading
    88	        </span>
    89	      </section>
    90	
    91	      <section
    92	        id="workbench-wow-starters"
    93	        class="workbench-wow-starters"
    94	        aria-label="Canonical demo scenarios — one-click starter cards"
    95	      >
    96	        <header class="workbench-wow-starters-header">
    97	          <p class="eyebrow">主流场景</p>
    98	          <h2>起手卡 · One-click 走读</h2>
    99	          <p class="workbench-wow-starters-sub">
   100	            预填 BEAT_DEEP_PAYLOAD / Monte-Carlo / Reverse-Diagnose 入口，落地 wow_a/b/c demo 弧。
   101	          </p>
   102	        </header>
   103	        <div class="workbench-wow-starters-grid">
   104	          <article
   105	            class="workbench-wow-card"
   106	            data-wow-id="wow_a"
   107	            aria-labelledby="workbench-wow-a-title"
   108	          >
   109	            <header>
   110	              <span class="workbench-wow-tag">wow_a</span>
   111	              <h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>
   112	            </header>
   113	            <p class="workbench-wow-card-desc">
   114	              POST <code>/api/lever-snapshot</code> with BEAT_DEEP_PAYLOAD (tra=-35°, n1k=0.92,
   115	              deploy=95%, feedback_mode=auto_scrubber) — under auto_scrubber pullback the
   116	              gates that latch are L2/L3/L4 (L1 drops out as reverser_not_deployed_eec
   117	              flips false mid-deploy, per <code>tests/e2e/test_wow_a_causal_chain.py</code>).
   118	            </p>
   119	            <button
   120	              type="button"
   121	              class="workbench-wow-run-button"
   122	              data-wow-action="run"
   123	              data-wow-id="wow_a"
   124	            >
   125	              一键运行 wow_a
   126	            </button>
   127	            <div
   128	              class="workbench-wow-result"
   129	              data-wow-result-for="wow_a"
   130	              role="status"
   131	              aria-live="polite"
   132	            >
   133	              尚未运行。
   134	            </div>
   135	          </article>
   136	          <article
   137	            class="workbench-wow-card"
   138	            data-wow-id="wow_b"
   139	            aria-labelledby="workbench-wow-b-title"
   140	          >
   141	            <header>
   142	              <span class="workbench-wow-tag">wow_b</span>
   143	              <h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>
   144	            </header>
   145	            <p class="workbench-wow-card-desc">
   146	              POST <code>/api/monte-carlo/run</code> with seed=42 — 1000 次抽样，输出
   147	              success_rate + failure_modes 分布。
   148	            </p>
   149	            <button
   150	              type="button"
   151	              class="workbench-wow-run-button"
   152	              data-wow-action="run"
   153	              data-wow-id="wow_b"
   154	            >
   155	              一键运行 wow_b
   156	            </button>
   157	            <div
   158	              class="workbench-wow-result"
   159	              data-wow-result-for="wow_b"
   160	              role="status"
   161	              aria-live="polite"
   162	            >
   163	              尚未运行。
   164	            </div>
   165	          </article>
   166	          <article
   167	            class="workbench-wow-card"
   168	            data-wow-id="wow_c"
   169	            aria-labelledby="workbench-wow-c-title"
   170	          >
   171	            <header>
   172	              <span class="workbench-wow-tag">wow_c</span>
   173	              <h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>
   174	            </header>
   175	            <p class="workbench-wow-card-desc">
   176	              POST <code>/api/diagnosis/run</code> with outcome=deploy_confirmed — 反求
   177	              触发该 outcome 的参数组合（max_results=10）。
   178	            </p>
   179	            <button
   180	              type="button"
   181	              class="workbench-wow-run-button"
   182	              data-wow-action="run"
   183	              data-wow-id="wow_c"
   184	            >
   185	              一键运行 wow_c
   186	            </button>
   187	            <div
   188	              class="workbench-wow-result"
   189	              data-wow-result-for="wow_c"
   190	              role="status"
   191	              aria-live="polite"
   192	            >
   193	              尚未运行。
   194	            </div>
   195	          </article>
   196	        </div>
   197	      </section>
   198	
   199	      <aside
   200	        id="workbench-trust-banner"
   201	        class="workbench-trust-banner"
   202	        data-feedback-mode="manual_feedback_override"
   203	        role="note"
   204	        aria-label="Feedback mode trust affordance"
   205	      >
   206	        <span class="workbench-trust-banner-icon" aria-hidden="true">⚠</span>
   207	        <div class="workbench-trust-banner-body">
   208	          <span class="workbench-trust-banner-scope">
   209	            <em>这里"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入用来覆盖某个观测读数的任何值——例如在运行一个场景前编辑快照输入字段
   210	            (any value you type into the workbench to override an observed reading — for example, editing a snapshot input field before running a scenario).
   211	            被动读取、回放与审计链导航不算 manual feedback (Passive reads, replays, and audit-chain navigation do NOT count as manual feedback).
   212	          </span>
   213	          <strong>该模式仅作参考 · That mode is advisory.</strong>
   214	          <span>
   215	            真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative.
   216	            你的手动反馈会被记录用于 diff / review，但不改写真值 · Your manual feedback is recorded for diff/review but does not change source-of-truth values.
   217	          </span>
   218	        </div>
   219	        <button
   220	          type="button"
   221	          class="workbench-trust-banner-dismiss"
   222	          aria-label="Hide trust banner for this session"
   223	          data-trust-banner-dismiss
   224	        >
   225	          隐藏（本次会话）· Hide for session
   226	        </button>
   227	      </aside>
   228	
   229	      <section id="workbench-annotation-toolbar" class="workbench-annotation-toolbar" aria-label="Annotation tools">
   230	        <span class="workbench-annotation-toolbar-label">标注</span>
   231	        <button type="button" class="workbench-annotation-tool is-active" data-annotation-tool="point">标记信号</button>
   232	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="area">圈选 logic gate</button>
   233	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="link">关联 spec</button>
   234	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="text-range">引用 requirement 段</button>
   235	        <span id="workbench-annotation-active-tool" class="workbench-annotation-active-tool" aria-live="polite">
   236	          标记信号 工具激活
   237	        </span>
   238	      </section>
   239	
   240	      <aside
   241	        id="workbench-authority-banner"
   242	        class="workbench-authority-banner"
   243	        role="note"
   244	        aria-label="Truth-engine authority contract"
   245	      >
   246	        <span class="workbench-authority-banner-icon" aria-hidden="true">🔒</span>
   247	        <span class="workbench-authority-banner-headline">
   248	          真值引擎 · 只读 · Truth Engine — Read Only
   249	        </span>
   250	        <span class="workbench-authority-banner-sep" aria-hidden="true">·</span>
   251	        <span class="workbench-authority-banner-rule">
   252	          Propose 不修改 · 工程师只能提交 ticket / proposal，不能直接改真值
   253	        </span>
   254	        <a
   255	          class="workbench-authority-banner-link"
   256	          href="/v6.1-redline"
   257	          target="_blank"
   258	          rel="noopener"
   259	          title="v6.1 truth-engine red line — sourced from .planning/constitution.md"
   260	        >
   261	          v6.1 红线条款 →
   262	        </a>
   263	      </aside>
   264	
   265	      <section class="workbench-collab-grid" aria-label="Three-column collaboration workbench">
   266	        <article
   267	          id="workbench-control-panel"
   268	          class="workbench-collab-column workbench-annotation-surface"
   269	          data-column="control"
   270	          data-annotation-surface="control"
   271	          tabindex="0"
   272	        >
   273	          <header>
   274	            <p class="eyebrow">probe &amp; trace</p>
   275	            <h2>探针与追踪 · Probe &amp; Trace</h2>
   276	          </header>
   277	          <div id="workbench-control-status" class="workbench-collab-status" aria-live="polite">
   278	            等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.
   279	          </div>
   280	          <div class="workbench-collab-control-list" aria-label="Control panel skeleton">
   281	            <button type="button" class="workbench-toolbar-button is-primary">加载当前工单 · Load Active Ticket</button>
   282	            <button type="button" class="workbench-toolbar-button">快照当前状态 · Snapshot Current State</button>
   283	          </div>
   284	        </article>
   285	
   286	        <article
   287	          id="workbench-document-panel"
   288	          class="workbench-collab-column workbench-annotation-surface"
   289	          data-column="document"
   290	          data-annotation-surface="document"
   291	          tabindex="0"
   292	        >
   293	          <header>
   294	            <p class="eyebrow">annotate &amp; propose</p>
   295	            <h2>标注与提案 · Annotate &amp; Propose</h2>
   296	          </header>
   297	          <div id="workbench-document-status" class="workbench-collab-status" aria-live="polite">
   298	            等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.
   299	          </div>
   300	          <div class="workbench-collab-document">
   301	            <p>参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes, and future text-range annotations will land here.</p>
   302	            <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>
   303	          </div>
   304	        </article>
   305	
   306	        <article
   307	          id="workbench-circuit-panel"
   308	          class="workbench-collab-column workbench-annotation-surface"
   309	          data-column="circuit"
   310	          data-annotation-surface="circuit"
   311	          tabindex="0"
   312	        >
   313	          <header>
   314	            <p class="eyebrow">hand off &amp; track</p>
   315	            <h2>移交与跟踪 · Hand off &amp; Track</h2>
   316	          </header>
   317	          <div id="workbench-circuit-status" class="workbench-collab-status" aria-live="polite">
   318	            等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot.
   319	          </div>
   320	          <div class="workbench-collab-circuit" aria-label="Circuit skeleton">
   321	            <span>SW1</span>
   322	            <span>Logic 1</span>
   323	            <span>Logic 2</span>
   324	            <span>Logic 3</span>
   325	            <span>Logic 4</span>
   326	            <span>THR LOCK</span>
   327	          </div>
   328	        </article>
   329	      </section>
   330	
   331	      <aside id="annotation-inbox" class="workbench-annotation-inbox" aria-label="Annotation Inbox">
   332	        <header>
   333	          <p class="eyebrow">标注收件箱</p>
   334	          <h2>审核队列 · Review Queue</h2>
   335	        </header>
   336	        <ul id="annotation-inbox-list">
   337	          <li>暂无已提交提案 · No proposals submitted yet.</li>
   338	        </ul>
   339	      </aside>
   340	
   341	      <footer id="workbench-bottom-bar" class="workbench-collab-bottom-bar" aria-label="Workbench actions">
   342	        <button
   343	          id="approval-center-entry"
   344	          type="button"
   345	          class="workbench-toolbar-button"
   346	          data-role="KOGAMI"
   347	          aria-controls="approval-center-panel"
   348	        >
   349	          审批中心 · Approval Center
   350	        </button>
   351	        <span>审批操作仅限 Kogami · Approval actions are Kogami-only.</span>
   352	      </footer>
   353	
   354	      <section
   355	        id="workbench-pending-signoff-affordance"
   356	        class="workbench-pending-signoff"
   357	        role="status"
   358	        aria-live="polite"
   359	        data-pending-signoff="hidden"
   360	      >
   361	        <span class="workbench-pending-signoff-icon" aria-hidden="true">🛈</span>
   362	        <div class="workbench-pending-signoff-body">
   363	          <strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>
   364	          <span>
   365	            你的提案已加入排队，等待 Kogami 处理。Approval 操作是 Kogami 专属
   366	            authority — 你的角色当前不会看到 disabled UI，而是这条 explicit
   367	            "排队中" 提示。
   368	          </span>
   369	        </div>
   370	      </section>
   371	
   372	      <section
   373	        id="approval-center-panel"
   374	        class="workbench-approval-center"
   375	        data-approval-role="KOGAMI"
   376	        aria-labelledby="approval-center-title"
   377	      >
   378	        <header>
   379	          <p class="eyebrow">审批中心</p>
   380	          <h2 id="approval-center-title">Kogami 提案审批 · Kogami Proposal Triage</h2>
   381	        </header>
   382	        <div class="workbench-approval-grid">
   383	          <article class="workbench-approval-lane" data-approval-lane="pending">
   384	            <h3>待审 · Pending</h3>
   385	            <p>已提交的标注提案在被通过或驳回前在此排队 · Submitted annotation proposals wait here before acceptance or rejection.</p>
   386	          </article>
   387	          <article class="workbench-approval-lane" data-approval-lane="accept">
   388	            <h3>通过 · Accept</h3>
   389	            <button type="button" class="workbench-toolbar-button" data-approval-action="accept">通过提案 · Accept Proposal</button>
   390	          </article>
   391	          <article class="workbench-approval-lane" data-approval-lane="reject">
   392	            <h3>驳回 · Reject</h3>
   393	            <button type="button" class="workbench-toolbar-button" data-approval-action="reject">驳回提案 · Reject Proposal</button>
   394	          </article>
   395	        </div>
   396	      </section>
   397	
   398	      <!-- E11-09 (2026-04-25): legacy "Workbench Bundle 验收台" content moved to /workbench/bundle. This page is now the Epic-06..10 shell only. -->
   399	    </main>
   400	
   401	    <script src="/annotation_overlay.js"></script>
   402	    <script src="/workbench.js"></script>
   403	  </body>
   404	</html>

exec
/bin/zsh -lc 'rg -n "closes 22 surfaces|PR body|feat/e11-15e|pull request|the last|all English surfaces|uniformly Chinese-first" .planning src tests -S' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:244:     4	**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:275:    35	E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:286:     5	**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:353:    72	E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:367:    86	**Surface-honesty pledge:** This sub-phase closes 22 surfaces. It does NOT close
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:368:    87	"all" or "the last". The deferred list above is **non-exhaustive** — if a
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:396:   115	| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:420:   139	fallback in PR body + `dev_handoff.md` + this inventory's persona-rotation
tests/test_workbench_approval_flow_polish.py:10:earlier docstring overclaimed "Closes the last English-only surface" —
tests/test_workbench_approval_flow_polish.py:189:    `uniformly Chinese-first`. P2 verified `/workbench` still has many
tests/test_workbench_approval_flow_polish.py:214:        "uniformly Chinese-first",
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-04-output.md:1625:+> **Persona selection: P5 (Apps Engineer)** — domain-anchoring is exactly the customer/repro lens this relabel is meant to serve; P5 round-robin slot also follows P2 (the last Tier-B was E11-14 = P2; round-robin successor is P3, but E11-13 was P1 and E11-14 was P2 — actually next is P3). However content-fit weight: P3 (Demo Presenter) is a better content match for "domain-anchored vocabulary the engineer/customer reads on screen". Plan defers to round-robin: **P3 Demo Presenter**.
tests/e2e/test_wow_a_causal_chain.py:22:#            AND reverser_not_deployed_eec; the last condition flips False once the
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R3-output.md:121:38:New helper `_final_verdict_block(text)` returns ONLY the text after the last `tokens used\nNNNN` marker (codex's session-tail canonical block). Three behavior changes:
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R3-output.md:196:898:    """Return only the text AFTER the last `tokens used\\nNNNN` marker.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R3-output.md:242:1319:    96	    """Return only the text AFTER the last `tokens used\\nNNNN` marker.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R3-output.md:374:2201:+    """Return only the text AFTER the last `tokens used\\nNNNN` marker.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R3-output.md:909:    96	    """Return only the text AFTER the last `tokens used\\nNNNN` marker.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R3-output.md:1008:   195	        # Legacy fallback: scope to after the last verdict marker.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R3-output.md:1408:   898	    """Return only the text AFTER the last `tokens used\\nNNNN` marker.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:7633:    22	#            AND reverser_not_deployed_eec; the last condition flips False once the
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:49:> 每个子 phase 结束前，必须在该子 phase 的 PR body 或专属 SURFACE-INVENTORY.md 里补完此表。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:116:> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:7154:    22	#            AND reverser_not_deployed_eec; the last condition flips False once the
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:135:**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:166:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:552:   118	    counting in the LAST verdict block (everything after the last
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:556:   122	    # Find the last verdict marker; count findings after that point only.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:906:   208	    as the next persona since E11-11 is the last Tier-B entry."""
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:30:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:44:`PERSONA-ROTATION-STATE.md` line 24: rewrote E11-15d entry to remove "Closes the last English-only surface" + "uniformly Chinese-first"; added "P2 R1 IMPORTANT closure" note + same deferred-to-E11-15e list.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:48:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:61:- **Did R2 actually close the overclaim?** Re-grep the inventory + rotation-state for `last English-only surface` / `uniformly Chinese-first` outside the leading blockquote and confirm zero hits.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:399:    10	> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:504:     3	Closes the last English-only surface in the workbench demo (the
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:679:   178	    claimed `last English-only surface` and `uniformly Chinese-first`,
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:696:   195	        "uniformly Chinese-first",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1108:/bin/zsh -lc 'rg -n "last English-only surface|uniformly Chinese-first" .planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/test_workbench_approval_flow_polish.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1110:tests/test_workbench_approval_flow_polish.py:3:Closes the last English-only surface in the workbench demo (the
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1111:tests/test_workbench_approval_flow_polish.py:178:    claimed `last English-only surface` and `uniformly Chinese-first`,
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1113:tests/test_workbench_approval_flow_polish.py:195:        "uniformly Chinese-first",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1115:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1124:One real issue is already visible: the docs were corrected, but the test module’s own header comment still says “Closes the last English-only surface,” which is the same overclaim R1 objected to. I’m checking the rest of the page for whether the deferred list is complete or still understates the remaining English-first surfaces.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1507:print('uniformly Chinese-first' in text)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1681:- **IMPORTANT** — [tests/test_workbench_approval_flow_polish.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_approval_flow_polish.py:1): R2 does not fully close the R1 doc-honesty issue. The module header still says this slice “Closes the last English-only surface,” while the new guard at [tests/test_workbench_approval_flow_polish.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_approval_flow_polish.py:176) only scans `E11-15d-SURFACE-INVENTORY.md` for two literal phrases. The same overclaim therefore still ships in-branch, and the guard is too narrow to catch it there or to catch equivalent rephrasings elsewhere.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1685:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1705:- **IMPORTANT** — [tests/test_workbench_approval_flow_polish.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_approval_flow_polish.py:1): R2 does not fully close the R1 doc-honesty issue. The module header still says this slice “Closes the last English-only surface,” while the new guard at [tests/test_workbench_approval_flow_polish.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_approval_flow_polish.py:176) only scans `E11-15d-SURFACE-INVENTORY.md` for two literal phrases. The same overclaim therefore still ships in-branch, and the guard is too narrow to catch it there or to catch equivalent rephrasings elsewhere.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1709:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
src/well_harness/static/c919_etras_panel/circuit.html:411:       inside the box; previously the last row overflowed the bottom. -->
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:320:**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:351:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt:12:Closes the LAST English-only surface in the workbench demo. With this sub-phase, `/workbench` is uniformly Chinese-first; only the backend API remediation message in `demo_server.py:743` stays English (backend contract, locked by `tests/test_lever_snapshot_manual_override_guard.py:151`).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt:38:- **Closure claim verification**: I claim `/workbench` is now uniformly Chinese-first. Verify by `grep -nE ">[A-Za-z][^<]*</h[1-3]>|>[A-Za-z][^<]*</button>"` on `workbench.html` to confirm no remaining English-only h1/h2/h3/button content. Acceptable exceptions: identifier strings in topbar chips (`Identity`, `Ticket`, `System`, `Feedback Mode`), system option labels (`Thrust Reverser`, etc.) which are domain proper-nouns, and the `eyebrow` decorative labels in the column trio (locked by E11-03 tests).
tests/test_codex_persona_dispatch.py:208:    as the next persona since E11-11 is the last Tier-B entry."""
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:1390:    22	#            AND reverser_not_deployed_eec; the last condition flips False once the
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:31:- **IMPORTANT** — `tests/test_workbench_approval_flow_polish.py:1`: R2 doesn't fully close the R1 doc-honesty issue. The module header still says this slice "Closes the last English-only surface," while the new guard at `:176` only scanned `E11-15d-SURFACE-INVENTORY.md` for two literal phrases. Same overclaim still shipped in-branch; guard too narrow.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:39:- Module docstring rewritten — removed "Closes the last English-only surface", added P2 R2 IMPORTANT closure note, expanded out-of-scope list to include all surfaces P2 enumerated.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:60:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-26-SUMMARY.md:4:- The workbench now restores the last packet workspace after bootstrap when browser storage is available, instead of always dropping users back onto the reference packet.
.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:27:Closes the LAST English-only surface in the workbench demo. With this sub-phase, `/workbench` is uniformly Chinese-first; only the backend API remediation message in `demo_server.py:743` stays English (backend contract, locked by `tests/test_lever_snapshot_manual_override_guard.py:151`).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:53:- **Closure claim verification**: I claim `/workbench` is now uniformly Chinese-first. Verify by `grep -nE ">[A-Za-z][^<]*</h[1-3]>|>[A-Za-z][^<]*</button>"` on `workbench.html` to confirm no remaining English-only h1/h2/h3/button content. Acceptable exceptions: identifier strings in topbar chips (`Identity`, `Ticket`, `System`, `Feedback Mode`), system option labels (`Thrust Reverser`, etc.) which are domain proper-nouns, and the `eyebrow` decorative labels in the column trio (locked by E11-03 tests).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:412:     3	Closes the last English-only surface in the workbench demo (the
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1093:+Closes the last English-only surface in the workbench demo (the
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1470:     5	> Closes the last English-only surface in the workbench demo: the
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1541:    76	With E11-15d, the entire `/workbench` UI is uniformly Chinese-first:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1577:    24	E11-15d: Tier-B (Persona = P2 — Senior FCS Engineer — round-robin successor of E11-10's P1 (derived programmatically by next-persona tool). Closes the last English-only surface in the workbench demo (3 approval lane h3s + 2 lane buttons + 1 pending-lane body copy). 6 [REWRITE], <10 copy_diff → Tier-B. Persona-content fit: P2's lens on visible-copy consistency works for this final approval-flow surface. With this sub-phase, /workbench is uniformly Chinese-first — only backend API remediation message in demo_server.py:743 stays English (backend contract).)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1900:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1915:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-prompt.txt:23:New helper `_final_verdict_block(text)` returns ONLY the text after the last `tokens used\nNNNN` marker (codex's session-tail canonical block). Three behavior changes:
.planning/constitution.md:348:**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/constitution.md:357:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/constitution.md:404:- **R5:** mandatory `drift-acceptance` declaration in PR body listing every outstanding cross-doc delta Codex flagged (using §3.1 standard template phrasing, no superlatives)
.planning/constitution.md:405:- **R6:** hard cap, binary author choice — (a) rollback to a smaller bundle, OR (b) merge-with-explicit-drift signed by author (PR body must contain the drift-acceptance list)
.planning/constitution.md:415:允许跳过 Codex round 2 直接 apply 修复的条件，五条全部满足：(1) 修复逐行 diff-level 匹配 Codex `Suggested fix` bullet；(2) 总改动 ≤20 LOC；(3) 触及 ≤2 个文件；(4) 不改动任何 public API surface；(5) PR body 显式引用 round number + finding ID。
.planning/constitution.md:419:任何触发 EMPIRICAL-CLAIM-PROBE 软/硬规则的 PR body 必须含 `external_gate_self_estimated_pass_rate: <0..1>`。低估 / 高估都进 retro 计分。
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:644:+> uniformly Chinese-first while preserving English suffixes for existing
.planning/audit/AUDIT-20260425-claude-pr5-round1-plant-deploy-blindspot.md:74:**Going forward (v6.1):** every PR opening prose that includes a numeric runtime claim ships with `external_gate_self_estimated_pass_rate: <0..1>` in the PR body so Codex round-1 outcomes can be calibrated against pre-submit confidence.
.planning/codex_personas/README.md:116:1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:15:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:29:`PERSONA-ROTATION-STATE.md` line 24: rewrote E11-15d entry to remove "Closes the last English-only surface" + "uniformly Chinese-first"; added "P2 R1 IMPORTANT closure" note + same deferred-to-E11-15e list.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:33:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:46:- **Did R2 actually close the overclaim?** Re-grep the inventory + rotation-state for `last English-only surface` / `uniformly Chinese-first` outside the leading blockquote and confirm zero hits.
.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md:8:> uniformly Chinese-first while preserving English suffixes for existing
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:8662:    22	#            AND reverser_not_deployed_eec; the last condition flips False once the
.planning/retrospectives/RETRO-V61-055-recursive-coherence-drift-on-rule-bundle-prs.md:88:- **R5**: mandatory `drift-acceptance` declaration in PR body listing every outstanding cross-doc delta Codex flagged (using §3.1 standard template phrasing, no superlatives)
.planning/retrospectives/RETRO-V61-055-recursive-coherence-drift-on-rule-bundle-prs.md:91:  - (b) merge-with-explicit-drift signed by author (PR body must contain the drift-acceptance list)
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:38:New helper `_final_verdict_block(text)` returns ONLY the text after the last `tokens used\nNNNN` marker (codex's session-tail canonical block). Three behavior changes:
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:748:    as the next persona since E11-11 is the last Tier-B entry."""
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:898:    """Return only the text AFTER the last `tokens used\\nNNNN` marker.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:997:        # Legacy fallback: scope to after the last verdict marker.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:1319:    96	    """Return only the text AFTER the last `tokens used\\nNNNN` marker.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:1418:   195	        # Legacy fallback: scope to after the last verdict marker.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:1856:   208	    as the next persona since E11-11 is the last Tier-B entry."""
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:2201:+    """Return only the text AFTER the last `tokens used\\nNNNN` marker.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:2287:-    counting in the LAST verdict block (everything after the last
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:2292:-    # Find the last verdict marker; count findings after that point only.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:2313:+        # Legacy fallback: scope to after the last verdict marker.
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:197:- Codex round logs (R1–R4): captured in branch `feat/E11-02-workbench-start-onboarding-20260425` PR body and merge `384901e`
.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:4:**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:35:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/E11-04-SURFACE-INVENTORY.md:32:> **Persona selection: P5 (Apps Engineer)** — domain-anchoring is exactly the customer/repro lens this relabel is meant to serve; P5 round-robin slot also follows P2 (the last Tier-B was E11-14 = P2; round-robin successor is P3, but E11-13 was P1 and E11-14 was P2 — actually next is P3). However content-fit weight: P3 (Demo Presenter) is a better content match for "domain-anchored vocabulary the engineer/customer reads on screen". Plan defers to round-robin: **P3 Demo Presenter**.
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:5:**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:72:E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:86:**Surface-honesty pledge:** This sub-phase closes 22 surfaces. It does NOT close
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:87:"all" or "the last". The deferred list above is **non-exhaustive** — if a
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:115:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:139:fallback in PR body + `dev_handoff.md` + this inventory's persona-rotation
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:16:- **IMPORTANT** — `tests/test_workbench_approval_flow_polish.py:1`: R2 doesn't fully close the R1 doc-honesty issue. The module header still says this slice "Closes the last English-only surface," while the new guard at `:176` only scanned `E11-15d-SURFACE-INVENTORY.md` for two literal phrases. Same overclaim still shipped in-branch; guard too narrow.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:24:- Module docstring rewritten — removed "Closes the last English-only surface", added P2 R2 IMPORTANT closure note, expanded out-of-scope list to include all surfaces P2 enumerated.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:45:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:1162:#            AND reverser_not_deployed_eec; the last condition flips False once the
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:323:**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:354:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:367:**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:434:E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:448:**Surface-honesty pledge:** This sub-phase closes 22 surfaces. It does NOT close
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:449:"all" or "the last". The deferred list above is **non-exhaustive** — if a
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:477:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:501:fallback in PR body + `dev_handoff.md` + this inventory's persona-rotation
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1348:tests/test_workbench_approval_flow_polish.py:189:    `uniformly Chinese-first`. P2 verified `/workbench` still has many
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1349:tests/test_workbench_approval_flow_polish.py:214:        "uniformly Chinese-first",
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1351:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1377:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:115:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1379:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:45:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1467:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:60:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1512:.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md:8:> uniformly Chinese-first while preserving English suffixes for existing
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1534:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:27:Closes the LAST English-only surface in the workbench demo. With this sub-phase, `/workbench` is uniformly Chinese-first; only the backend API remediation message in `demo_server.py:743` stays English (backend contract, locked by `tests/test_lever_snapshot_manual_override_guard.py:151`).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1536:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:53:- **Closure claim verification**: I claim `/workbench` is now uniformly Chinese-first. Verify by `grep -nE ">[A-Za-z][^<]*</h[1-3]>|>[A-Za-z][^<]*</button>"` on `workbench.html` to confirm no remaining English-only h1/h2/h3/button content. Acceptable exceptions: identifier strings in topbar chips (`Identity`, `Ticket`, `System`, `Feedback Mode`), system option labels (`Thrust Reverser`, etc.) which are domain proper-nouns, and the `eyebrow` decorative labels in the column trio (locked by E11-03 tests).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1540:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1541:    76	With E11-15d, the entire `/workbench` UI is uniformly Chinese-first:
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1544:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1577:    24	E11-15d: Tier-B (Persona = P2 — Senior FCS Engineer — round-robin successor of E11-10's P1 (derived programmatically by next-persona tool). Closes the last English-only surface in the workbench demo (3 approval lane h3s + 2 lane buttons + 1 pending-lane body copy). 6 [REWRITE], <10 copy_diff → Tier-B. Persona-content fit: P2's lens on visible-copy consistency works for this final approval-flow surface. With this sub-phase, /workbench is uniformly Chinese-first — only backend API remediation message in demo_server.py:743 stays English (backend contract).)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1546:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1900:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1548:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1915:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1576:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:5:You ran the E11-15d Tier-B review across 3 rounds (R1, R2, R3) and were the persona who flagged the doc-honesty `last English-only surface` / `uniformly Chinese-first` overclaim. Your enumeration of remaining English-only surfaces in E11-15d's R2 review is what E11-15e set out to close.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1577:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:15:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1578:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:16:   - Any forbidden overclaim phrases (`last English-only surface` / `uniformly Chinese-first` / `all English surfaces` / equivalents) that drifted in?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1585:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:644:+> uniformly Chinese-first while preserving English suffixes for existing
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1593:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:30:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1597:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:44:`PERSONA-ROTATION-STATE.md` line 24: rewrote E11-15d entry to remove "Closes the last English-only surface" + "uniformly Chinese-first"; added "P2 R1 IMPORTANT closure" note + same deferred-to-E11-15e list.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1598:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:48:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1599:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:61:- **Did R2 actually close the overclaim?** Re-grep the inventory + rotation-state for `last English-only surface` / `uniformly Chinese-first` outside the leading blockquote and confirm zero hits.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1603:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:399:    10	> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1610:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:679:   178	    claimed `last English-only surface` and `uniformly Chinese-first`,
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1611:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:696:   195	        "uniformly Chinese-first",
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1615:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1108:/bin/zsh -lc 'rg -n "last English-only surface|uniformly Chinese-first" .planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/test_workbench_approval_flow_polish.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1616:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1111:tests/test_workbench_approval_flow_polish.py:178:    claimed `last English-only surface` and `uniformly Chinese-first`,
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1617:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1113:tests/test_workbench_approval_flow_polish.py:195:        "uniformly Chinese-first",
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1618:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1115:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1619:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1507:print('uniformly Chinese-first' in text)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1620:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1685:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1621:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1709:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1632:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt:12:Closes the LAST English-only surface in the workbench demo. With this sub-phase, `/workbench` is uniformly Chinese-first; only the backend API remediation message in `demo_server.py:743` stays English (backend contract, locked by `tests/test_lever_snapshot_manual_override_guard.py:151`).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1634:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt:38:- **Closure claim verification**: I claim `/workbench` is now uniformly Chinese-first. Verify by `grep -nE ">[A-Za-z][^<]*</h[1-3]>|>[A-Za-z][^<]*</button>"` on `workbench.html` to confirm no remaining English-only h1/h2/h3/button content. Acceptable exceptions: identifier strings in topbar chips (`Identity`, `Ticket`, `System`, `Feedback Mode`), system option labels (`Thrust Reverser`, etc.) which are domain proper-nouns, and the `eyebrow` decorative labels in the column trio (locked by E11-03 tests).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1646:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:20:You ran the E11-15d Tier-B review across 3 rounds (R1, R2, R3) and were the persona who flagged the doc-honesty `last English-only surface` / `uniformly Chinese-first` overclaim. Your enumeration of remaining English-only surfaces in E11-15d's R2 review is what E11-15e set out to close.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1647:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:30:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1648:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:31:   - Any forbidden overclaim phrases (`last English-only surface` / `uniformly Chinese-first` / `all English surfaces` / equivalents) that drifted in?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1659:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:263:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1661:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:292:/bin/zsh -lc 'pwd && git rev-parse --short HEAD && git status --short && rg -n "E11-15e|E11-15d|LogicMVP|persona|surface-inventory|uniformly Chinese-first|last English-only surface" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1808:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:477:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1819:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:15:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1823:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:29:`PERSONA-ROTATION-STATE.md` line 24: rewrote E11-15d entry to remove "Closes the last English-only surface" + "uniformly Chinese-first"; added "P2 R1 IMPORTANT closure" note + same deferred-to-E11-15e list.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1824:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:33:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1825:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:46:- **Did R2 actually close the overclaim?** Re-grep the inventory + rotation-state for `last English-only surface` / `uniformly Chinese-first` outside the leading blockquote and confirm zero hits.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:20:You ran the E11-15d Tier-B review across 3 rounds (R1, R2, R3) and were the persona who flagged the doc-honesty `last English-only surface` / `uniformly Chinese-first` overclaim. Your enumeration of remaining English-only surfaces in E11-15d's R2 review is what E11-15e set out to close.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:30:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:31:   - Any forbidden overclaim phrases (`last English-only surface` / `uniformly Chinese-first` / `all English surfaces` / equivalents) that drifted in?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:80:**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:111:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:153:**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:220:E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:234:**Surface-honesty pledge:** This sub-phase closes 22 surfaces. It does NOT close
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:235:"all" or "the last". The deferred list above is **non-exhaustive** — if a
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:263:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:287:fallback in PR body + `dev_handoff.md` + this inventory's persona-rotation
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:292:/bin/zsh -lc 'pwd && git rev-parse --short HEAD && git status --short && rg -n "E11-15e|E11-15d|LogicMVP|persona|surface-inventory|uniformly Chinese-first|last English-only surface" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:381:    `uniformly Chinese-first`. P2 verified `/workbench` still has many
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:406:        "uniformly Chinese-first",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:695:/bin/zsh -lc 'rg -n "last English-only surface|uniformly Chinese-first|all English surfaces|all English-only|uniformly|the last|Chinese-first" -S .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md tests/test_workbench_e11_15e_chinese_first_bundle.py .planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md .planning/phases/E11-workbench-engineer-first-ux/persona-P*-E11-15e-output.md .planning/phases/E11-workbench-engineer-first-ux/persona-P*-E11-15e-prompt.txt src/well_harness/static/workbench.html src/well_harness/static/workbench.js' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:700:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:72:E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:701:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:87:"all" or "the last". The deferred list above is **non-exhaustive** — if a
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:702:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:115:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:704:.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:35:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:714:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:5:You ran the E11-15d Tier-B review across 3 rounds (R1, R2, R3) and were the persona who flagged the doc-honesty `last English-only surface` / `uniformly Chinese-first` overclaim. Your enumeration of remaining English-only surfaces in E11-15d's R2 review is what E11-15e set out to close.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:715:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:15:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:716:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:16:   - Any forbidden overclaim phrases (`last English-only surface` / `uniformly Chinese-first` / `all English surfaces` / equivalents) that drifted in?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:719:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:166:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:720:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:20:You ran the E11-15d Tier-B review across 3 rounds (R1, R2, R3) and were the persona who flagged the doc-honesty `last English-only surface` / `uniformly Chinese-first` overclaim. Your enumeration of remaining English-only surfaces in E11-15d's R2 review is what E11-15e set out to close.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:721:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:30:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:722:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:31:   - Any forbidden overclaim phrases (`last English-only surface` / `uniformly Chinese-first` / `all English surfaces` / equivalents) that drifted in?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:723:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:111:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:729:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:220:E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:730:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:235:"all" or "the last". The deferred list above is **non-exhaustive** — if a
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:731:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:263:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:733:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:292:/bin/zsh -lc 'pwd && git rev-parse --short HEAD && git status --short && rg -n "E11-15e|E11-15d|LogicMVP|persona|surface-inventory|uniformly Chinese-first|last English-only surface" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:740:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:354:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:742:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:434:E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:743:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:449:"all" or "the last". The deferred list above is **non-exhaustive** — if a
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:744:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:477:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:753:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1348:tests/test_workbench_approval_flow_polish.py:189:    `uniformly Chinese-first`. P2 verified `/workbench` still has many
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:754:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1349:tests/test_workbench_approval_flow_polish.py:214:        "uniformly Chinese-first",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:756:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1351:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:767:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1377:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:115:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:769:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1379:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:45:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:797:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1467:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:60:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:823:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1512:.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md:8:> uniformly Chinese-first while preserving English suffixes for existing
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:827:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1534:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:27:Closes the LAST English-only surface in the workbench demo. With this sub-phase, `/workbench` is uniformly Chinese-first; only the backend API remediation message in `demo_server.py:743` stays English (backend contract, locked by `tests/test_lever_snapshot_manual_override_guard.py:151`).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:829:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1536:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:53:- **Closure claim verification**: I claim `/workbench` is now uniformly Chinese-first. Verify by `grep -nE ">[A-Za-z][^<]*</h[1-3]>|>[A-Za-z][^<]*</button>"` on `workbench.html` to confirm no remaining English-only h1/h2/h3/button content. Acceptable exceptions: identifier strings in topbar chips (`Identity`, `Ticket`, `System`, `Feedback Mode`), system option labels (`Thrust Reverser`, etc.) which are domain proper-nouns, and the `eyebrow` decorative labels in the column trio (locked by E11-03 tests).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:832:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1540:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1541:    76	With E11-15d, the entire `/workbench` UI is uniformly Chinese-first:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:835:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1544:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1577:    24	E11-15d: Tier-B (Persona = P2 — Senior FCS Engineer — round-robin successor of E11-10's P1 (derived programmatically by next-persona tool). Closes the last English-only surface in the workbench demo (3 approval lane h3s + 2 lane buttons + 1 pending-lane body copy). 6 [REWRITE], <10 copy_diff → Tier-B. Persona-content fit: P2's lens on visible-copy consistency works for this final approval-flow surface. With this sub-phase, /workbench is uniformly Chinese-first — only backend API remediation message in demo_server.py:743 stays English (backend contract).)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:837:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1546:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1900:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:839:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1548:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1915:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:846:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1576:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:5:You ran the E11-15d Tier-B review across 3 rounds (R1, R2, R3) and were the persona who flagged the doc-honesty `last English-only surface` / `uniformly Chinese-first` overclaim. Your enumeration of remaining English-only surfaces in E11-15d's R2 review is what E11-15e set out to close.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:847:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1577:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:15:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:848:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1578:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:16:   - Any forbidden overclaim phrases (`last English-only surface` / `uniformly Chinese-first` / `all English surfaces` / equivalents) that drifted in?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:854:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1585:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:644:+> uniformly Chinese-first while preserving English suffixes for existing
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:861:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1593:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:30:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:865:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1597:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:44:`PERSONA-ROTATION-STATE.md` line 24: rewrote E11-15d entry to remove "Closes the last English-only surface" + "uniformly Chinese-first"; added "P2 R1 IMPORTANT closure" note + same deferred-to-E11-15e list.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:866:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1598:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:48:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:867:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1599:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:61:- **Did R2 actually close the overclaim?** Re-grep the inventory + rotation-state for `last English-only surface` / `uniformly Chinese-first` outside the leading blockquote and confirm zero hits.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:870:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1603:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:399:    10	> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:873:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1610:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:679:   178	    claimed `last English-only surface` and `uniformly Chinese-first`,
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:874:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1611:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:696:   195	        "uniformly Chinese-first",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:878:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1615:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1108:/bin/zsh -lc 'rg -n "last English-only surface|uniformly Chinese-first" .planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/test_workbench_approval_flow_polish.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:879:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1616:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1111:tests/test_workbench_approval_flow_polish.py:178:    claimed `last English-only surface` and `uniformly Chinese-first`,
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:880:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1617:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1113:tests/test_workbench_approval_flow_polish.py:195:        "uniformly Chinese-first",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:881:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1618:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1115:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:882:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1619:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1507:print('uniformly Chinese-first' in text)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:883:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1620:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1685:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:884:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1621:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1709:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:886:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1632:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt:12:Closes the LAST English-only surface in the workbench demo. With this sub-phase, `/workbench` is uniformly Chinese-first; only the backend API remediation message in `demo_server.py:743` stays English (backend contract, locked by `tests/test_lever_snapshot_manual_override_guard.py:151`).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:888:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1634:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt:38:- **Closure claim verification**: I claim `/workbench` is now uniformly Chinese-first. Verify by `grep -nE ">[A-Za-z][^<]*</h[1-3]>|>[A-Za-z][^<]*</button>"` on `workbench.html` to confirm no remaining English-only h1/h2/h3/button content. Acceptable exceptions: identifier strings in topbar chips (`Identity`, `Ticket`, `System`, `Feedback Mode`), system option labels (`Thrust Reverser`, etc.) which are domain proper-nouns, and the `eyebrow` decorative labels in the column trio (locked by E11-03 tests).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:896:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1646:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:20:You ran the E11-15d Tier-B review across 3 rounds (R1, R2, R3) and were the persona who flagged the doc-honesty `last English-only surface` / `uniformly Chinese-first` overclaim. Your enumeration of remaining English-only surfaces in E11-15d's R2 review is what E11-15e set out to close.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:897:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1647:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:30:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:898:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1648:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:31:   - Any forbidden overclaim phrases (`last English-only surface` / `uniformly Chinese-first` / `all English surfaces` / equivalents) that drifted in?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:904:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1659:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:263:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:906:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1661:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:292:/bin/zsh -lc 'pwd && git rev-parse --short HEAD && git status --short && rg -n "E11-15e|E11-15d|LogicMVP|persona|surface-inventory|uniformly Chinese-first|last English-only surface" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:944:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1808:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:477:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:952:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1819:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:15:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:956:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1823:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:29:`PERSONA-ROTATION-STATE.md` line 24: rewrote E11-15d entry to remove "Closes the last English-only surface" + "uniformly Chinese-first"; added "P2 R1 IMPORTANT closure" note + same deferred-to-E11-15e list.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:957:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1824:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:33:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:958:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1825:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:46:- **Did R2 actually close the overclaim?** Re-grep the inventory + rotation-state for `last English-only surface` / `uniformly Chinese-first` outside the leading blockquote and confirm zero hits.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:985:{+**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`+}
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1052:{+E11-15e is **NOT** "the last English-only surface" on `/workbench`. The+}
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1066:{+**Surface-honesty pledge:** This sub-phase closes 22 surfaces. It does NOT close+}
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1067:{+"all" or "the last". The deferred list above is **non-exhaustive** — if a+}
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1095:{+| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |+}
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1119:{+fallback in PR body + `dev_handoff.md` + this inventory's persona-rotation+}
.planning/phases/governance-bundle-2/codex-r2-output.md:242:.planning/codex_personas/README.md:46:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:325:+**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r2-output.md:335:+读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:516: 允许跳过 Codex round 2 直接 apply 修复的条件，五条全部满足：(1) 修复逐行 diff-level 匹配 Codex `Suggested fix` bullet；(2) 总改动 ≤20 LOC；(3) 触及 ≤2 个文件；(4) 不改动任何 public API surface；(5) PR body 显式引用 round number + finding ID。
.planning/phases/governance-bundle-2/codex-r2-output.md:520: 任何触发 EMPIRICAL-CLAIM-PROBE 软/硬规则的 PR body 必须含 `external_gate_self_estimated_pass_rate: <0..1>`。低估 / 高估都进 retro 计分。
.planning/phases/governance-bundle-2/codex-r2-output.md:630:   371	允许跳过 Codex round 2 直接 apply 修复的条件，五条全部满足：(1) 修复逐行 diff-level 匹配 Codex `Suggested fix` bullet；(2) 总改动 ≤20 LOC；(3) 触及 ≤2 个文件；(4) 不改动任何 public API surface；(5) PR body 显式引用 round number + finding ID。
.planning/phases/governance-bundle-2/codex-r2-output.md:669:    36	**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r2-output.md:679:    46	读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:778:.planning/codex_personas/README.md:46:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:809:.planning/phases/governance-bundle-2/codex-r2-output.md:242:.planning/codex_personas/README.md:46:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:828:.planning/phases/governance-bundle-2/codex-r2-output.md:335:+读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:1069:.planning/phases/governance-bundle-2/codex-r2-output.md:242:.planning/codex_personas/README.md:46:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:1073:.planning/phases/governance-bundle-2/codex-r2-output.md:335:+读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:1077:.planning/phases/governance-bundle-2/codex-r2-output.md:679:    46	读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:1082:.planning/phases/governance-bundle-2/codex-r2-output.md:778:.planning/codex_personas/README.md:46:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:1089:.planning/phases/governance-bundle-2/codex-r2-output.md:809:.planning/phases/governance-bundle-2/codex-r2-output.md:242:.planning/codex_personas/README.md:46:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:1093:.planning/phases/governance-bundle-2/codex-r2-output.md:828:.planning/phases/governance-bundle-2/codex-r2-output.md:335:+读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:1102:.planning/codex_personas/README.md:46:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:5:You ran the E11-15d Tier-B review across 3 rounds (R1, R2, R3) and were the persona who flagged the doc-honesty `last English-only surface` / `uniformly Chinese-first` overclaim. Your enumeration of remaining English-only surfaces in E11-15d's R2 review is what E11-15e set out to close.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:15:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:16:   - Any forbidden overclaim phrases (`last English-only surface` / `uniformly Chinese-first` / `all English surfaces` / equivalents) that drifted in?
.planning/phases/governance-bundle-2/codex-r5-output.md:474:   345	**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r5-output.md:493:   147	- Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows. "copy diff ≥10 lines" is computed by `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` (X+Y from the last summary line); the number is printed in PR body for reviewer reproducibility.
.planning/phases/governance-bundle-2/codex-r5-output.md:513:    42	**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r5-output.md:523:    52	读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r5-output.md:649:    49	> 每个子 phase 结束前，必须在该子 phase 的 PR body 或专属 SURFACE-INVENTORY.md 里补完此表。
.planning/phases/governance-bundle-2/codex-r5-output.md:716:   116	> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/governance-bundle-2/codex-r5-output.md:979:   136	1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
.planning/phases/governance-bundle-2/codex-r5-output.md:1027:.planning/codex_personas/README.md:136:1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-15-PLAN.md:5:Let control-plane maintenance slices advance the latest verified plan without accidentally downgrading the visible QA baseline from the last full shared validation run.
.planning/STATE.md:586:- `P6-15 保留更强的共享验证基线` is now implemented locally: focused control-plane maintenance runs can advance the latest verified plan and latest success run, while repo/notion snapshots keep carrying forward the last richer shared validation baseline instead of collapsing QA confidence down to a narrow `1/1 shared validation checks pass`.
.planning/STATE.md:603:- `P7-12` is now implemented locally: the browser workbench exposes one-click acceptance presets for ready, blocked, quick-preview, and archive-retry flows, and the frontend now treats the last clicked preset as the winning result so rapid multi-clicks do not repaint stale output.
.planning/STATE.md:722:- Make recent archive recovery discoverable too, so engineers can reopen the last few archive packages directly from the workbench without first copying local paths out of the filesystem.
.planning/phases/governance-bundle-2/codex-r6-output.md:458:   116	1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
.planning/phases/governance-bundle-2/codex-r6-output.md:524:    49	> 每个子 phase 结束前，必须在该子 phase 的 PR body 或专属 SURFACE-INVENTORY.md 里补完此表。
.planning/phases/governance-bundle-2/codex-r6-output.md:591:   116	> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/governance-bundle-2/codex-r6-output.md:839:   345	**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r6-output.md:848:   354	读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r6-output.md:880:116:1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
.planning/phases/governance-bundle-2/codex-r6-output.md:889:116:> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/governance-bundle-2/codex-r6-output.md:922:.planning/constitution.md:345:**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r6-output.md:923:.planning/constitution.md:354:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r6-output.md:942:.planning/codex_personas/README.md:116:1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
.planning/phases/governance-bundle-2/codex-r6-output.md:952:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:116:> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/governance-bundle-2/codex-r6-output.md:1001:-**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r6-output.md:1011:-读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r6-output.md:1099:-- Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows. "copy diff ≥10 lines" is computed by `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` (X+Y from the last summary line); the number is printed in PR body for reviewer reproducibility.
.planning/phases/governance-bundle-2/codex-r6-output.md:1189:   116	1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
.planning/phases/governance-bundle-2/codex-r6-output.md:1341:.planning/codex_personas/README.md:116:1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
.planning/phases/governance-bundle-2/codex-r4-output.md:348: **"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r4-output.md:358: 读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r4-output.md:423:+1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
.planning/phases/governance-bundle-2/codex-r4-output.md:487: **"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r4-output.md:496: 读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r4-output.md:524: 允许跳过 Codex round 2 直接 apply 修复的条件，五条全部满足：(1) 修复逐行 diff-level 匹配 Codex `Suggested fix` bullet；(2) 总改动 ≤20 LOC；(3) 触及 ≤2 个文件；(4) 不改动任何 public API surface；(5) PR body 显式引用 round number + finding ID。
.planning/phases/governance-bundle-2/codex-r4-output.md:532: > **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/governance-bundle-2/codex-r4-output.md:677: - Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows. "copy diff ≥10 lines" is computed by `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` (X+Y from the last summary line); the number is printed in PR body for reviewer reproducibility.
.planning/phases/governance-bundle-2/codex-r4-output.md:750:   345	**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r4-output.md:759:   354	读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r4-output.md:816:   147	- Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows. "copy diff ≥10 lines" is computed by `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` (X+Y from the last summary line); the number is printed in PR body for reviewer reproducibility.
.planning/phases/governance-bundle-2/codex-r4-output.md:852:    42	**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r4-output.md:862:    52	读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r4-output.md:926:   116	1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
.planning/phases/governance-bundle-2/codex-r4-output.md:1019:.planning/codex_personas/README.md:116:1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
.planning/phases/governance-bundle-2/codex-r3-output.md:115:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:147:- Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows. "copy diff ≥10 lines" is computed by `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` (X+Y from the last summary line); the number is printed in PR body for reviewer reproducibility.
.planning/phases/governance-bundle-2/codex-r3-output.md:130:.planning/codex_personas/README.md:52:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r3-output.md:159:.planning/constitution.md:354:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r3-output.md:169:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:116:> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/governance-bundle-2/codex-r3-output.md:246:    42	**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r3-output.md:256:    52	读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r3-output.md:347:   147	- Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows. "copy diff ≥10 lines" is computed by `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` (X+Y from the last summary line); the number is printed in PR body for reviewer reproducibility.
.planning/phases/governance-bundle-2/codex-r3-output.md:395:   345	**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r3-output.md:404:   354	读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r3-output.md:432:   382	允许跳过 Codex round 2 直接 apply 修复的条件，五条全部满足：(1) 修复逐行 diff-level 匹配 Codex `Suggested fix` bullet；(2) 总改动 ≤20 LOC；(3) 触及 ≤2 个文件；(4) 不改动任何 public API surface；(5) PR body 显式引用 round number + finding ID。
.planning/phases/governance-bundle-2/codex-r3-output.md:436:   386	任何触发 EMPIRICAL-CLAIM-PROBE 软/硬规则的 PR body 必须含 `external_gate_self_estimated_pass_rate: <0..1>`。低估 / 高估都进 retro 计分。
.planning/phases/governance-bundle-2/codex-r3-output.md:734:+**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r3-output.md:743:+读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r3-output.md:1054:+- Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows. "copy diff ≥10 lines" is computed by `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` (X+Y from the last summary line); the number is printed in PR body for reviewer reproducibility.
.planning/phases/governance-bundle-2/codex-r3-output.md:1204:    36	**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r3-output.md:1214:    46	读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-08-SUMMARY.md:5:`P6-08` removes the last major readability drift in the active control-plane surfaces: successful validation evidence is now summarized in short human-readable lines, repo-side handoff docs stay slim, and the Notion sync loop no longer dies just because one of the active status-style pages has drifted into an archived block state.
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:1498:   345	**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:1507:   354	读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:1535:   382	允许跳过 Codex round 2 直接 apply 修复的条件，五条全部满足：(1) 修复逐行 diff-level 匹配 Codex `Suggested fix` bullet；(2) 总改动 ≤20 LOC；(3) 触及 ≤2 个文件；(4) 不改动任何 public API surface；(5) PR body 显式引用 round number + finding ID。
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:1539:   386	任何触发 EMPIRICAL-CLAIM-PROBE 软/硬规则的 PR body 必须含 `external_gate_self_estimated_pass_rate: <0..1>`。低估 / 高估都进 retro 计分。
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:1601:    42	**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:1611:    52	读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:1704:   147	- Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows. "copy diff ≥10 lines" is computed by `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` (X+Y from the last summary line); the number is printed in PR body for reviewer reproducibility.
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:1790:    49	> 每个子 phase 结束前，必须在该子 phase 的 PR body 或专属 SURFACE-INVENTORY.md 里补完此表。
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:1857:   116	> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-11-SUMMARY.md:5:`P6-11` removes the last obvious repo-side lag inside P6: when the dashboard already reflects a fresher GitHub-backed snapshot than the locally visible Notion databases, repo-side handoff and freeze docs now follow the dashboard instead of getting stuck on stale database state.
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-20-PLAN.md:9:- `P6-18` fixed active-page link drift and `P6-19` removed the last stale bootstrap examples, but the control plane still churns page IDs because `replace_active_sync_page()` creates a fresh child page whenever the rendered content changes.
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-19-PLAN.md:5:Remove the last concrete stale project-state examples from the repo-side Notion bootstrap guide so it can only be read as a historical/reference template, not as a live status source.
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-26-PLAN.md:21:- Refreshing the workbench restores the last packet workspace instead of always dropping back to the default reference sample.
.planning/phases/05-demo-polish-and-edge-case-hardening/05-07-SUMMARY.md:5:`P5-07` corrected the last interaction mismatch in the demo cockpit: the TRA slider now always shows the full `-32° .. 0°` visual range, but free dragging stays inside `-14° .. 0°` until the `L4` boundary unlock is ready. The desktop cockpit was also rebalanced so the lever deck, presets, and condition area feel less crowded while keeping VDT adjustment and the right-side logic board readable together.

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '3768,3800p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  3768	// (e.g., when the snapshot endpoint reports a different mode in future
  3769	// E11-14+). Banner dismissal is session-local (sessionStorage); chip + actual
  3770	// mode value remain visible across dismissals.
  3771	function syncTrustBannerForMode(mode) {
  3772	  const banner = document.getElementById("workbench-trust-banner");
  3773	  if (banner) {
  3774	    banner.setAttribute("data-feedback-mode", mode);
  3775	  }
  3776	}
  3777	
  3778	function setFeedbackMode(mode) {
  3779	  const allowed = new Set(["manual_feedback_override", "truth_engine"]);
  3780	  if (!allowed.has(mode)) {
  3781	    return false;
  3782	  }
  3783	  const chip = document.getElementById("workbench-feedback-mode");
  3784	  if (chip) {
  3785	    chip.setAttribute("data-feedback-mode", mode);
  3786	    const label = chip.querySelector("strong");
  3787	    if (label) {
  3788	      label.textContent = mode === "truth_engine" ? "真值引擎 · Truth Engine" : "手动（仅参考）· Manual (advisory)";
  3789	    }
  3790	  }
  3791	  syncTrustBannerForMode(mode);
  3792	  return true;
  3793	}
  3794	
  3795	function installFeedbackModeAffordance() {
  3796	  const chip = document.getElementById("workbench-feedback-mode");
  3797	  const banner = document.getElementById("workbench-trust-banner");
  3798	  if (!chip || !banner) {
  3799	    return;
  3800	  }

exec
/bin/zsh -lc "nl -ba tests/test_workbench_e11_15e_chinese_first_bundle.py | sed -n '1,260p' && printf '\\n---\\n' && nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""E11-15e — Tier-A Chinese-first bundle regression lock.
     2	
     3	Bilingualizes 17 user-visible English-only surfaces enumerated by P2
     4	during the E11-15d review (see test_workbench_approval_flow_polish.py
     5	docstring Section 7 + .planning/phases/E11-workbench-engineer-first-ux/
     6	E11-15d-SURFACE-INVENTORY.md):
     7	
     8	  Topbar chips (5):       身份/工单/反馈模式/系统 + Manual (advisory) chip
     9	  WOW h3 direction (3):   Causal Chain / Monte Carlo / Reverse Diagnose
    10	  State-of-world (5):     truth-engine SHA / recent e2e / adversarial /
    11	                          open issues / advisory flag
    12	  Trust banner body (3):  scope <em>, advisory <strong>, truth-engine <span>
    13	  Authority banner (1):   Truth Engine — Read Only headline
    14	  Trust dismiss (1):      Hide for session button
    15	  Boot placeholders (3):  pre-hydration "Waiting for ... panel boot."
    16	  Reference packet (1):   Annotate column intro <p>
    17	  Inbox empty (1):        No proposals submitted yet.
    18	  Pending sign-off (1):   Pending Kogami sign-off
    19	
    20	Pattern: `<中文> · <English>` everywhere; English suffix is preserved
    21	verbatim so all prior `assert <english> in html` substring locks across
    22	test_workbench_trust_affordance, test_workbench_authority_banner,
    23	test_workbench_role_affordance, test_workbench_column_rename, and
    24	test_workbench_state_of_world_bar continue to pass without contract
    25	churn.
    26	
    27	Out of scope (deferred to a future Tier-A or constitutional decision):
    28	  - <option> system values (`Thrust Reverser`, `Landing Gear`, etc.) —
    29	    domain proper nouns coupled to value-attribute IDs and to the
    30	    multi-system adapter dispatch in tests/test_p19_api_multisystem.py.
    31	  - Post-hydration JS boot status strings (`Probe & Trace ready. ...`)
    32	    locked by tests/test_workbench_column_rename.py:170-172 — those are
    33	    a separate JS-side bilingualization with their own lockstep contract.
    34	  - <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge
    35	    </pre> flow diagram — visual phase-arrow, not English copy.
    36	  - Workbench-bundle / approval-center / annotation-toolbar surfaces
    37	    that were already bilingualized in earlier sub-phases.
    38	
    39	Test-tier rationale: ≥15 REWRITE strings → Tier-A per the constitution.
    40	"""
    41	
    42	from __future__ import annotations
    43	
    44	import http.client
    45	import threading
    46	from http.server import ThreadingHTTPServer
    47	from pathlib import Path
    48	
    49	import pytest
    50	
    51	from well_harness.demo_server import DemoRequestHandler
    52	
    53	
    54	REPO_ROOT = Path(__file__).resolve().parents[1]
    55	STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
    56	
    57	
    58	def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    59	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    60	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    61	    thread.start()
    62	    return server, thread
    63	
    64	
    65	def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    66	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    67	    connection.request("GET", path)
    68	    response = connection.getresponse()
    69	    return response.status, response.read().decode("utf-8")
    70	
    71	
    72	@pytest.fixture
    73	def server():
    74	    s, t = _start_demo_server()
    75	    try:
    76	        yield s
    77	    finally:
    78	        s.shutdown()
    79	        s.server_close()
    80	        t.join(timeout=2)
    81	
    82	
    83	# ─── 1. Bilingualized strings POSITIVELY locked ──────────────────────
    84	
    85	
    86	@pytest.mark.parametrize(
    87	    "bilingual",
    88	    [
    89	        # Topbar chip labels (5)
    90	        "<span>身份 · Identity</span>",
    91	        "<span>工单 · Ticket</span>",
    92	        "<span>反馈模式 · Feedback Mode</span>",
    93	        "<span>系统 · System</span>",
    94	        "<strong>手动（仅参考）· Manual (advisory)</strong>",
    95	        # WOW h3 direction flips (3) — Chinese-first per E11-15c convention
    96	        '<h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>',
    97	        '<h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>',
    98	        '<h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>',
    99	        # State-of-world labels (4) + advisory flag (1)
   100	        "真值引擎 SHA · truth-engine SHA",
   101	        "最近 e2e · recent e2e",
   102	        "对抗样本 · adversarial",
   103	        "未关闭问题 · open issues",
   104	        "仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading",
   105	        # Trust banner body (3)
   106	        '这里"手动反馈"的含义 · What "manual feedback" means here:',
   107	        "该模式仅作参考 · That mode is advisory.",
   108	        "真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings",
   109	        # Trust banner dismiss (1)
   110	        "隐藏（本次会话）· Hide for session",
   111	        # Authority banner headline (1)
   112	        "真值引擎 · 只读 · Truth Engine — Read Only",
   113	        # Pre-hydration boot placeholders (3)
   114	        "等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.",
   115	        "等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.",
   116	        "等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot.",
   117	        # Reference-packet intro (1)
   118	        "参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes",
   119	        # Inbox empty state (1)
   120	        "暂无已提交提案 · No proposals submitted yet.",
   121	        # Pending sign-off (1)
   122	        "等待 Kogami 签字 · Pending Kogami sign-off",
   123	    ],
   124	)
   125	def test_workbench_html_carries_bilingual_e11_15e_string(bilingual: str) -> None:
   126	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   127	    assert bilingual in html, f"missing E11-15e bilingual string: {bilingual}"
   128	
   129	
   130	# ─── 2. Stale English-only surfaces are gone ─────────────────────────
   131	
   132	
   133	@pytest.mark.parametrize(
   134	    "stale",
   135	    [
   136	        # Bare topbar chip labels (no Chinese prefix) — must be replaced
   137	        "<span>Identity</span>",
   138	        "<span>Ticket</span>",
   139	        "<span>Feedback Mode</span>",
   140	        "<span>System</span>",
   141	        "<strong>Manual (advisory)</strong>",
   142	        # WOW h3 stale English-first ordering (E11-15c convention)
   143	        '<h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>',
   144	        '<h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>',
   145	        '<h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>',
   146	        # Bare state-of-world labels (no Chinese prefix)
   147	        ">truth-engine SHA<",
   148	        ">recent e2e<",
   149	        ">adversarial<",
   150	        ">open issues<",
   151	        # Bare trust-banner body lines — these are now sentence-internal
   152	        # so we look for the line-leading position they used to hold.
   153	        "<em>What \"manual feedback\" means here:</em>",
   154	        "<strong>That mode is advisory.</strong>",
   155	        # Bare button + headline + boot placeholders
   156	        ">\n          Hide for session\n        <",
   157	        ">\n          Truth Engine — Read Only\n        <",
   158	        ">\n            Waiting for probe &amp; trace panel boot.\n          <",
   159	        ">\n            Waiting for annotate &amp; propose panel boot.\n          <",
   160	        ">\n            Waiting for hand off &amp; track panel boot.\n          <",
   161	        # Bare inbox + pending sign-off
   162	        "<li>No proposals submitted yet.</li>",
   163	        "<strong>Pending Kogami sign-off</strong>",
   164	    ],
   165	)
   166	def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
   167	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   168	    assert stale not in html, f"stale English-only surface still present: {stale}"
   169	
   170	
   171	# ─── 3. English suffixes preserved (substring locks unchanged) ───────
   172	
   173	
   174	@pytest.mark.parametrize(
   175	    "preserved_english_suffix",
   176	    [
   177	        # Anchors required by trust_affordance.py
   178	        "Manual (advisory)",
   179	        "Truth engine readings",
   180	        "Hide for session",
   181	        'What "manual feedback" means here',
   182	        "That mode is advisory.",
   183	        # Anchor required by authority_banner.py
   184	        "Truth Engine — Read Only",
   185	        # Anchor required by role_affordance.py
   186	        "Pending Kogami sign-off",
   187	        # Anchor required by state_of_world_bar.py
   188	        "advisory · not a live truth-engine reading",
   189	        # Anchors required by column_rename.py:118-120 (pre-hydration)
   190	        "Waiting for probe &amp; trace panel boot.",
   191	        "Waiting for annotate &amp; propose panel boot.",
   192	        "Waiting for hand off &amp; track panel boot.",
   193	    ],
   194	)
   195	def test_e11_15e_preserves_english_suffix_locks(preserved_english_suffix: str) -> None:
   196	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   197	    assert preserved_english_suffix in html, (
   198	        f"E11-15e broke English-suffix substring lock: {preserved_english_suffix}"
   199	    )
   200	
   201	
   202	# ─── 4. Structural anchors preserved ─────────────────────────────────
   203	
   204	
   205	@pytest.mark.parametrize(
   206	    "anchor",
   207	    [
   208	        'id="workbench-feedback-mode"',
   209	        'id="workbench-trust-banner"',
   210	        'id="workbench-authority-banner"',
   211	        'id="workbench-pending-signoff-affordance"',
   212	        'id="workbench-state-of-world-bar"',
   213	        'id="workbench-wow-starters"',
   214	        'data-trust-banner-dismiss',
   215	        'data-feedback-mode="manual_feedback_override"',
   216	    ],
   217	)
   218	def test_e11_15e_preserves_structural_anchors(anchor: str) -> None:
   219	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   220	    assert anchor in html, f"E11-15e broke structural anchor: {anchor}"
   221	
   222	
   223	# ─── 5. workbench.js feedback-mode chip stays in lockstep with HTML ──
   224	
   225	
   226	def test_workbench_js_feedback_mode_label_is_bilingualized() -> None:
   227	    """workbench.js:3788 dynamically rewrites the chip <strong> on mode
   228	    switch. If the JS literal stays English-only, the very first mode
   229	    flip would silently revert the static HTML's bilingual chip back to
   230	    `Manual (advisory)` / `Truth Engine`. Lock both branches."""
   231	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   232	    assert '"真值引擎 · Truth Engine"' in js, (
   233	        "JS feedback-mode `truth_engine` branch must use bilingual label"
   234	    )
   235	    assert '"手动（仅参考）· Manual (advisory)"' in js, (
   236	        "JS feedback-mode `manual_feedback_override` branch must use bilingual label"
   237	    )
   238	    # Stale English-only literals must not coexist (would imply duplicate
   239	    # write-paths or stale residue).
   240	    assert '"Truth Engine"' not in js, (
   241	        'stale English-only `"Truth Engine"` literal still in workbench.js'
   242	    )
   243	    assert '"Manual (advisory)"' not in js, (
   244	        'stale English-only `"Manual (advisory)"` literal still in workbench.js'
   245	    )
   246	
   247	
   248	# ─── 6. Live-served route reflects E11-15e end-to-end ────────────────
   249	
   250	
   251	def test_workbench_route_serves_e11_15e_bundle(server) -> None:
   252	    status, html = _get(server, "/workbench")
   253	    assert status == 200
   254	    # Spot-check one string from each surface category.
   255	    assert "身份 · Identity" in html
   256	    assert "因果链走读 · Causal Chain" in html
   257	    assert "真值引擎 SHA · truth-engine SHA" in html
   258	    assert "该模式仅作参考 · That mode is advisory." in html
   259	    assert "隐藏（本次会话）· Hide for session" in html
   260	    assert "真值引擎 · 只读 · Truth Engine — Read Only" in html

---
     1	# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY
     2	
     3	**Date:** 2026-04-26
     4	**Status:** in_review (Tier-A, ≥15 REWRITE rows → 5-persona dispatch)
     5	**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
     6	**Scope:** Bilingualize the user-visible English-only surfaces on `/workbench`
     7	that P2 enumerated during the E11-15d Tier-B review (see
     8	`tests/test_workbench_approval_flow_polish.py:189-194`).
     9	
    10	---
    11	
    12	## 1. Tier classification
    13	
    14	Per the constitution, Tier = **Tier-A** iff
    15	`copy_diff_lines ≥ 10 AND (REWRITE + DELETE) count ≥ 3`.
    16	
    17	| Metric | Count |
    18	|--------|------:|
    19	| copy_diff_lines (workbench.html + workbench.js)        | ~38 |
    20	| REWRITE rows (display strings rewritten in place)      | **22** |
    21	| DELETE rows (English-only string removed without bilingual replacement) | 0 |
    22	| ADD rows (new strings introduced for the first time)   | 0 |
    23	
    24	**Verdict: Tier-A.** Dispatch round-robin successor of E11-15d's P2 → **P3**, plus
    25	P1, P2, P4, P5 per Tier-A 5-persona requirement.
    26	
    27	---
    28	
    29	## 2. Surface table (REWRITE = 22)
    30	
    31	Pattern across all rows: `<中文> · <English>`. The English suffix is preserved
    32	verbatim so prior-sub-phase substring locks (`assert <english> in html`) keep
    33	passing without contract churn.
    34	
    35	| # | Surface | File:Line | Old (English-only) | New (bilingual) |
    36	|---|---------|-----------|---------------------|-----------------|
    37	| 1 | Identity chip label | workbench.html:26 | `<span>Identity</span>` | `<span>身份 · Identity</span>` |
    38	| 2 | Ticket chip label | workbench.html:30 | `<span>Ticket</span>` | `<span>工单 · Ticket</span>` |
    39	| 3 | Feedback Mode chip label | workbench.html:41 | `<span>Feedback Mode</span>` | `<span>反馈模式 · Feedback Mode</span>` |
    40	| 4 | Manual (advisory) chip text (HTML) | workbench.html:42 | `<strong>Manual (advisory)</strong>` | `<strong>手动（仅参考）· Manual (advisory)</strong>` |
    41	| 5 | Manual (advisory) chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Manual (advisory)"` literal | `"手动（仅参考）· Manual (advisory)"` |
    42	| 6 | Truth Engine chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Truth Engine"` literal | `"真值引擎 · Truth Engine"` |
    43	| 7 | System chip label | workbench.html:46 | `<span>System</span>` | `<span>系统 · System</span>` |
    44	| 8 | WOW h3 (wow_a) — direction flip | workbench.html:111 | `Causal Chain · 因果链走读` | `因果链走读 · Causal Chain` |
    45	| 9 | WOW h3 (wow_b) — direction flip | workbench.html:143 | `Monte Carlo · 1000-trial 可靠性` | `1000-trial 可靠性 · Monte Carlo` |
    46	| 10 | WOW h3 (wow_c) — direction flip | workbench.html:173 | `Reverse Diagnose · 反向诊断` | `反向诊断 · Reverse Diagnose` |
    47	| 11 | State-of-world label · sha | workbench.html:65 | `truth-engine SHA` | `真值引擎 SHA · truth-engine SHA` |
    48	| 12 | State-of-world label · e2e | workbench.html:71 | `recent e2e` | `最近 e2e · recent e2e` |
    49	| 13 | State-of-world label · adversarial | workbench.html:77 | `adversarial` | `对抗样本 · adversarial` |
    50	| 14 | State-of-world label · open issues | workbench.html:83 | `open issues` | `未关闭问题 · open issues` |
    51	| 15 | State-of-world advisory flag | workbench.html:87 | `advisory · not a live truth-engine reading` | `仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading` |
    52	| 16 | Trust banner scope `<em>` | workbench.html:209-211 | `<em>What "manual feedback" means here:</em> any value...` | `<em>这里"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入...` |
    53	| 17 | Trust banner advisory `<strong>` | workbench.html:213 | `<strong>That mode is advisory.</strong>` | `<strong>该模式仅作参考 · That mode is advisory.</strong>` |
    54	| 18 | Trust banner truth-engine `<span>` | workbench.html:215-217 | `Truth engine readings (logic gates L1–L4 ...)` | `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings ...` |
    55	| 19 | Trust banner dismiss button | workbench.html:225 | `Hide for session` | `隐藏（本次会话）· Hide for session` |
    56	| 20 | Authority banner headline | workbench.html:248 | `Truth Engine — Read Only` | `真值引擎 · 只读 · Truth Engine — Read Only` |
    57	| 21 | Pre-hydration boot status (control panel) | workbench.html:278 | `Waiting for probe & trace panel boot.` | `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` |
    58	| 22 | Pre-hydration boot status (document panel) | workbench.html:298 | `Waiting for annotate & propose panel boot.` | `等待 annotate & propose 面板启动 · Waiting for annotate & propose panel boot.` |
    59	| 23 | Pre-hydration boot status (circuit panel) | workbench.html:318 | `Waiting for hand off & track panel boot.` | `等待 hand off & track 面板启动 · Waiting for hand off & track panel boot.` |
    60	| 24 | Reference packet intro `<p>` | workbench.html:301 | `Reference packet, clarification notes...` | `参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, ...` |
    61	| 25 | Annotation inbox empty state | workbench.html:337 | `<li>No proposals submitted yet.</li>` | `<li>暂无已提交提案 · No proposals submitted yet.</li>` |
    62	| 26 | Pending sign-off `<strong>` | workbench.html:363 | `<strong>Pending Kogami sign-off</strong>` | `<strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>` |
    63	
    64	(22 rows after dedup of #5/#6 with their HTML siblings; the table uses 26 row IDs
    65	for line-of-evidence but treats #4+#5 and #11-#14+#15 as single `surface diff`
    66	counts in the metric table above.)
    67	
    68	---
    69	
    70	## 3. Out of scope (explicitly deferred — surface-honesty closure)
    71	
    72	E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
    73	following surfaces remain English-only and are **deferred to future sub-phases
    74	or constitutional decisions**, not silently included:
    75	
    76	| Deferred surface | Why deferred | File:Line |
    77	|------------------|--------------|-----------|
    78	| `<option>` system values (`Thrust Reverser`, `Landing Gear`, `Bleed Air Valve`, `C919 E-TRAS`) | Domain proper nouns coupled to value-attribute IDs and the multi-system adapter dispatch in `tests/test_p19_api_multisystem.py`. Bilingualizing the option text would require coordinated changes to value-id parsing, locale-mapping, and the adapter contract. | workbench.html:48-51 |
    79	| Post-hydration JS boot status strings (`Probe & Trace ready. Scenario actions are staged for the next bundle.` × 3) | Locked by `tests/test_workbench_column_rename.py:170-172`; would require workbench.js bilingualization with its own lockstep test contract. **Note:** This is the string users actually see for most of session — the "Waiting for ... panel boot." strings E11-15e bilingualizes are pre-hydration only. Re-tier as Tier-A for a follow-up sub-phase. | workbench.js boot fns |
    80	| `<pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>` | Visual phase-arrow diagram, not English copy. Would require a Chinese arrow notation decision (e.g. `承接 → 澄清 → 回放 → 诊断 → 知识`); deferred to UX/copy decision. | workbench.html:302 |
    81	| `data-wow-id="wow_a"` attribute strings + `data-wow-action="run"` | Internal data-* attributes, not user-visible — out of bilingualization scope by design. | workbench.html:104-194 |
    82	| `wow_a/b/c` tag spans (`<span class="workbench-wow-tag">wow_a</span>`) | Card identifier sigil, not display copy; these literally name the API endpoint group. | workbench.html:110/142/172 |
    83	| Eyebrow `probe & trace` / `annotate & propose` / `hand off & track` (lowercase column eyebrows) | These are paired with the bilingual `<h2>` titles E11-15c shipped (e.g. `<h2>探针与追踪 · Probe & Trace</h2>`). Eyebrows are intentionally English-only for the column-key tag pattern; if revisited, would need its own constitutional pass. | workbench.html:274/294/314 |
    84	| `WB-E06-SHELL` ticket id, `Kogami / Engineer` identity | Identifiers/proper nouns, not display copy. | workbench.html:27/31 |
    85	
    86	**Surface-honesty pledge:** This sub-phase closes 22 surfaces. It does NOT close
    87	"all" or "the last". The deferred list above is **non-exhaustive** — if a
    88	reviewer finds another English-only user-visible surface not listed here that is
    89	neither REWRITE in this slice nor in the deferred table, that finding is
    90	**legitimate** and a CHANGES_REQUIRED is appropriate.
    91	
    92	---
    93	
    94	## 4. Truth-engine red line
    95	
    96	Display-copy edits only. `controller.py` / `runner.py` / `models.py` /
    97	`src/well_harness/adapters/` / `demo_server.py` are **untouched**. Lockstep
    98	guard at `tests/test_workbench_e11_15e_chinese_first_bundle.py::
    99	test_e11_15e_does_not_touch_truth_engine_backend` scans backend files for any
   100	of the 23 Chinese display strings introduced here.
   101	
   102	---
   103	
   104	## 5. Lockstep test impact
   105	
   106	| Existing test file | Impact | Reason |
   107	|--------------------|--------|--------|
   108	| `test_workbench_trust_affordance.py` | ✅ no change | All 5 substring locks (`Manual (advisory)`, `Truth engine readings`, `Hide for session`, `What "manual feedback" means here`, `That mode is advisory.`) are preserved as English suffixes. |
   109	| `test_workbench_authority_banner.py` | ✅ no change | `Truth Engine — Read Only` preserved as suffix. |
   110	| `test_workbench_role_affordance.py` | ✅ no change | `Pending Kogami sign-off` preserved as suffix. |
   111	| `test_workbench_column_rename.py` | ✅ no change | Pre-hydration `Waiting for ... panel boot.` substrings preserved as suffixes; post-hydration JS strings unchanged (out of scope). |
   112	| `test_workbench_state_of_world_bar.py` | ✅ no change | `advisory · not a live truth-engine reading` preserved as suffix. |
   113	| `test_workbench_chinese_direction_consistency.py` | ✅ no change | E11-15c column h2 invariant unaffected (no h2 changes). |
   114	| `test_workbench_chinese_h2_button_sweep.py` | ✅ no change | h2/button sweep targets are already-bilingual surfaces. |
   115	| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
   116	| `test_workbench_e11_15e_chinese_first_bundle.py` (new) | ✅ added | 67 tests — positive bilingual locks, stale-English negative guards, English-suffix preservation locks, structural anchors, JS lockstep, live-served route, truth-engine red-line guard. |
   117	
   118	Full suite verification: **1221 passed, 0 regressions** (pre-PR baseline 1154).
   119	
   120	---
   121	
   122	## 6. Persona dispatch plan
   123	
   124	Tier-A → 5-persona round-robin. E11-15d closed with P2 → successor for E11-15e
   125	**lead** is **P3**.
   126	
   127	| Persona | Lens |
   128	|---------|------|
   129	| P1 | Engineer-task-flow regression |
   130	| P2 | Surface-inventory honesty + closure-claim guards |
   131	| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
   132	| P4 | Lockstep test contract preservation (no churn on existing locks) |
   133	| P5 | Truth-engine red-line + JS-HTML lockstep |
   134	
   135	**Codex degradation contingency:** if all 5 codex accounts are
   136	secondary-window-throttled or token-refresh-failed (as in E11-15d R3), apply
   137	**Executor 即 Gate (v3.2 治理折叠)** per the project memory rule:
   138	Claude Code Opus 4.7 self-signs the Tier-A gate, transparently documenting the
   139	fallback in PR body + `dev_handoff.md` + this inventory's persona-rotation
   140	entry. Self-signing requires the standard 1221-test green + repo-honesty self-
   141	review (this inventory + Section 3 surface-honesty pledge satisfy that bar).

web search: 
web search: 
codex
我已经把静态 HTML 和新测试逐行展开了。接下来补两块容易出真问题的证据：一是实际 `main..83d69e4` 的 Tier 计数，二是 `/workbench` 上尚存但未登记的英文表面，避免 inventory 只覆盖作者自报范围。
exec
/bin/zsh -lc "rg --files .planning | rg 'PR|pr|handoff|dev_handoff|pull|review packet|E11-15e'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-08-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-r2-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-r2-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-r2-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R3-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-r2-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-r3-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-03-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-r3-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-r2-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-r2-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-04-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-r2-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-prompt.txt
.planning/retrospectives/RETRO-V61-055-recursive-coherence-drift-on-rule-bundle-prs.md
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md
.planning/audit/bundles/p32-provenance-backfill-README.md
.planning/audit/bundles/p32-provenance-backfill.bundle
.planning/audit/AUDIT-20260425-claude-pr5-round1-plant-deploy-blindspot.md
.planning/phases/08-runtime-generalization-proof/08-04-SUMMARY.md
.planning/phases/08-runtime-generalization-proof/08-01-SUMMARY.md
.planning/phases/08-runtime-generalization-proof/08-01-PLAN.md
.planning/phases/08-runtime-generalization-proof/08-03-PLAN.md
.planning/phases/08-runtime-generalization-proof/08-06-SUMMARY.md
.planning/phases/08-runtime-generalization-proof/08-03-SUMMARY.md
.planning/phases/08-runtime-generalization-proof/08-02-PLAN.md
.planning/phases/08-runtime-generalization-proof/08-05-SUMMARY.md
.planning/phases/08-runtime-generalization-proof/08-06-PLAN.md
.planning/phases/08-runtime-generalization-proof/08-02-SUMMARY.md
.planning/phases/08-runtime-generalization-proof/08-04-PLAN.md
.planning/phases/08-runtime-generalization-proof/08-05-PLAN.md
.planning/PROJECT.md
.planning/codex_personas/P3-demo-presenter.md
.planning/phases/P38-c919-etras-provenance-closure/P38-05-CLOSURE.md
.planning/phases/P38-c919-etras-provenance-closure/P38-00-PLAN.md
.planning/phases/governance-bundle-2/codex-r3-prompt.txt
.planning/phases/governance-bundle-2/codex-r6-prompt.txt
.planning/phases/governance-bundle-2/codex-r3-retry-prompt.txt
.planning/phases/governance-bundle-2/codex-r4-prompt.txt
.planning/phases/governance-bundle-2/codex-r2-prompt.txt
.planning/phases/governance-bundle-2/codex-r5-prompt.txt
.planning/phases/E08-approval-center/E08-00-PLAN.md
.planning/phases/E08-approval-center/E08-05-CLOSURE.md
.planning/phases/P32-provenance-backfill/P32-00-PLAN.md
.planning/phases/P32-provenance-backfill/P32-05-CLOSURE.md
.planning/phases/E09-prompt-ticket-auth/E09-00-PLAN.md
.planning/phases/E09-prompt-ticket-auth/E09-05-CLOSURE.md
.planning/phases/P29-pre-pitch-readiness/P29-00-TIER1-PLAN.md
.planning/phases/E10-pr-review-close-loop/E10-00-PLAN.md
.planning/phases/E10-pr-review-close-loop/E10-05-CLOSURE.md
.planning/phases/P43-control-logic-workbench/reports/p43-01-contract-proof/CONTRACT-PROOF-REPORT.md

exec
/bin/zsh -lc "python3 - <<'PY'
from pathlib import Path
import re
html = Path('src/well_harness/static/workbench.html').read_text(encoding='utf-8')
# crude scan for visible text nodes with ASCII letters, excluding tags/attrs
# just emit interesting single-line spans/buttons/headings/pre/title snippets.
patterns = [
    r'>\\s*(["'^<>'"\\n]*[A-Za-z]["'^<>'"\\n]*)\\s*<',
]
seen=[]
for m in re.finditer(patterns[0], html):
    text=' '.join(m.group(1).split())
    if not text:
        continue
    if text in {'<"'!doctype html'"'}:
        continue
    if text not in seen:
        seen.append(text)
for text in seen:
    print(text)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
Control Logic Workbench
控制逻辑工作台 · Control Logic Workbench
身份 · Identity
Kogami / Engineer
工单 · Ticket
WB-E06-SHELL
反馈模式 · Feedback Mode
手动（仅参考）· Manual (advisory)
系统 · System
Thrust Reverser
Landing Gear
Bleed Air Valve
C919 E-TRAS
真值引擎 SHA · truth-engine SHA
最近 e2e · recent e2e
对抗样本 · adversarial
未关闭问题 · open issues
仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading
起手卡 · One-click 走读
预填 BEAT_DEEP_PAYLOAD / Monte-Carlo / Reverse-Diagnose 入口，落地 wow_a/b/c demo 弧。
wow_a
因果链走读 · Causal Chain
POST
/api/lever-snapshot
tests/e2e/test_wow_a_causal_chain.py
一键运行 wow_a
wow_b
1000-trial 可靠性 · Monte Carlo
/api/monte-carlo/run
一键运行 wow_b
wow_c
反向诊断 · Reverse Diagnose
/api/diagnosis/run
一键运行 wow_c
这里"手动反馈"的含义 · What "manual feedback" means here:
该模式仅作参考 · That mode is advisory.
隐藏（本次会话）· Hide for session
圈选 logic gate
关联 spec
引用 requirement 段
真值引擎 · 只读 · Truth Engine — Read Only
Propose 不修改 · 工程师只能提交 ticket / proposal，不能直接改真值
v6.1 红线条款 →
probe &amp; trace
探针与追踪 · Probe &amp; Trace
等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.
加载当前工单 · Load Active Ticket
快照当前状态 · Snapshot Current State
annotate &amp; propose
标注与提案 · Annotate &amp; Propose
等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.
参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes, and future text-range annotations will land here.
Knowledge
hand off &amp; track
移交与跟踪 · Hand off &amp; Track
等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot.
SW1
Logic 1
Logic 2
Logic 3
Logic 4
THR LOCK
审核队列 · Review Queue
暂无已提交提案 · No proposals submitted yet.
审批中心 · Approval Center
审批操作仅限 Kogami · Approval actions are Kogami-only.
等待 Kogami 签字 · Pending Kogami sign-off
Kogami 提案审批 · Kogami Proposal Triage
待审 · Pending
已提交的标注提案在被通过或驳回前在此排队 · Submitted annotation proposals wait here before acceptance or rejection.
通过 · Accept
通过提案 · Accept Proposal
驳回 · Reject
驳回提案 · Reject Proposal

exec
/bin/zsh -lc "git diff --stat main..83d69e4 -- 'src/well_harness/static/*.{html,js,css}' && printf '\\n---\\n' && git diff --stat "'$(git merge-base HEAD main)..83d69e4 -- '"'src/well_harness/static/*.{html,js,css}' && printf '\\n---\\n' && git diff --unified=0 main..83d69e4 -- src/well_harness/static/workbench.html src/well_harness/static/workbench.js | tail -n 5" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:

---

---
--- a/src/well_harness/static/workbench.js
+++ b/src/well_harness/static/workbench.js
@@ -3788 +3788 @@ function setFeedbackMode(mode) {
-      label.textContent = mode === "truth_engine" ? "Truth Engine" : "Manual (advisory)";
+      label.textContent = mode === "truth_engine" ? "真值引擎 · Truth Engine" : "手动（仅参考）· Manual (advisory)";

exec
/bin/zsh -lc 'python3 tools/codex_persona_dispatch.py next-persona' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
P3

exec
/bin/zsh -lc "python3 - <<'PY'
from pathlib import Path
import re
p = Path('src/well_harness/static/workbench.html')
for i,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
    for m in re.finditer(r'>(["'^<>]*[A-Za-z][''^<>]*)<'"', line):
        text=' '.join(m.group(1).split())
        if text:
            print(f'{i}: {text}')
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
6: Control Logic Workbench
18: 控制逻辑工作台 · Control Logic Workbench
26: 身份 · Identity
27: Kogami / Engineer
30: 工单 · Ticket
31: WB-E06-SHELL
41: 反馈模式 · Feedback Mode
42: 手动（仅参考）· Manual (advisory)
46: 系统 · System
48: Thrust Reverser
49: Landing Gear
50: Bleed Air Valve
51: C919 E-TRAS
65: 真值引擎 SHA · truth-engine SHA
71: 最近 e2e · recent e2e
77: 对抗样本 · adversarial
83: 未关闭问题 · open issues
98: 起手卡 · One-click 走读
110: wow_a
111: 因果链走读 · Causal Chain
114: /api/lever-snapshot
117: tests/e2e/test_wow_a_causal_chain.py
142: wow_b
143: 1000-trial 可靠性 · Monte Carlo
146: /api/monte-carlo/run
172: wow_c
173: 反向诊断 · Reverse Diagnose
176: /api/diagnosis/run
209: 这里"手动反馈"的含义 · What "manual feedback" means here:
213: 该模式仅作参考 · That mode is advisory.
232: 圈选 logic gate
233: 关联 spec
234: 引用 requirement 段
274: probe &amp; trace
275: 探针与追踪 · Probe &amp; Trace
281: 加载当前工单 · Load Active Ticket
282: 快照当前状态 · Snapshot Current State
294: annotate &amp; propose
295: 标注与提案 · Annotate &amp; Propose
301: 参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes, and future text-range annotations will land here.
302: Knowledge
314: hand off &amp; track
315: 移交与跟踪 · Hand off &amp; Track
321: SW1
322: Logic 1
323: Logic 2
324: Logic 3
325: Logic 4
326: THR LOCK
334: 审核队列 · Review Queue
337: 暂无已提交提案 · No proposals submitted yet.
351: 审批操作仅限 Kogami · Approval actions are Kogami-only.
363: 等待 Kogami 签字 · Pending Kogami sign-off
380: Kogami 提案审批 · Kogami Proposal Triage
384: 待审 · Pending
385: 已提交的标注提案在被通过或驳回前在此排队 · Submitted annotation proposals wait here before acceptance or rejection.
388: 通过 · Accept
389: 通过提案 · Accept Proposal
392: 驳回 · Reject
393: 驳回提案 · Reject Proposal

codex
仓库里没看到单独的 PR body 工件文件。我补做一次 `gh pr view 30` 探测；如果本机 GitHub 上下文可用，就直接按真实 PR 描述复核 overclaim，而不是只看 repo 内副本。
exec
/bin/zsh -lc 'gh pr view 30 --json number,title,body,headRefName,baseRefName' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 639ms:
{"baseRefName":"main","body":"## Summary\n\nE11-15e Tier-A bundle that bilingualizes 22 user-visible English-only surfaces on `/workbench` enumerated by P2 during the E11-15d Tier-B review.\n\n- **Pattern:** `<中文> · <English>` everywhere; English suffix preserved verbatim\n- **Lockstep contract:** zero churn on existing substring locks (test_workbench_trust_affordance, test_workbench_authority_banner, test_workbench_role_affordance, test_workbench_column_rename, test_workbench_state_of_world_bar)\n- **JS lockstep:** workbench.js:3788 dynamic chip text bilingualized so first mode switch doesn't revert to English\n- **Truth-engine red line:** controller.py / runner.py / models.py / adapters / demo_server.py untouched; new test scans backend for the 23 Chinese display strings\n\n## Surface scope\n\n22 REWRITE rows: topbar chips (5) + WOW h3 direction flips (3) + state-of-world labels (5) + trust banner body (3) + dismiss button + authority banner headline + pre-hydration boot placeholders (3) + reference packet intro + inbox empty state + pending sign-off.\n\n**Surface honesty:** This sub-phase closes 22 surfaces. It does **NOT** close \"the last\" or \"all\". Deferred surfaces (system options, post-hydration JS boot status, phase-arrow flow diagram, column eyebrow tags) are explicitly listed in SURFACE-INVENTORY.md Section 3 (non-exhaustive).\n\n## Tier classification\n\nTier-A per constitution: copy_diff_lines ~38, REWRITE rows = 22 (>=10 lines AND >=3 REWRITE).\n\nPersona dispatch: **P3** (round-robin successor of E11-15d's P2) leads, with P1/P2/P4/P5 per Tier-A 5-persona requirement.\n\n## Verification\n\n- New test file `tests/test_workbench_e11_15e_chinese_first_bundle.py`: **67 cases pass**\n- Full suite: **1221 passed, 0 regressions**\n\n## Test plan\n\n- [x] tests/test_workbench_e11_15e_chinese_first_bundle.py — 67/67 pass\n- [x] tests/test_workbench_*.py — 188/188 pass\n- [x] tests/ — 1221/1221 pass\n- [ ] Tier-A 5-persona codex dispatch; if codex degraded, Executor 即 Gate (v3.2) per project memory rule (documented in SURFACE-INVENTORY Section 6)\n\nGenerated with Claude Code","headRefName":"feat/e11-15e-tier-a-chinese-first-bundle-20260426","number":30,"title":"phase(E11-15e): Tier-A Chinese-first bundle — 22 REWRITE rows"}

exec
/bin/zsh -lc "git diff --stat main..83d69e4 -- src/well_harness/static/workbench.html src/well_harness/static/workbench.js && printf '\\n---\\n' && git diff --numstat main..83d69e4 -- src/well_harness/static/workbench.html src/well_harness/static/workbench.js" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
 src/well_harness/static/workbench.html | 54 +++++++++++++++++-----------------
 src/well_harness/static/workbench.js   |  2 +-
 2 files changed, 28 insertions(+), 28 deletions(-)

---
27	27	src/well_harness/static/workbench.html
1	1	src/well_harness/static/workbench.js

exec
/bin/zsh -lc 'rg -n "REWRITE|DELETE|Tier-A|copy diff" .planning/constitution.md .planning/codex_personas/README.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md -S' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/codex_personas/README.md:12:- **Tier-A (5-parallel):** within-PR inter-persona finding uniqueness (each persona must contribute ≥1 finding NOT mentioned by other 4) mitigates same-model bias.
.planning/codex_personas/README.md:31:> **Canonical rule definition lives in `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger.** This document does not redefine or paraphrase the rule. To know which tier fires, when to fire it, who selects the Tier-B persona, what the rollback condition is, or how to compute "copy diff ≥ 10 行" — read constitution. This README's only role in the rule layer is to point.
.planning/codex_personas/README.md:38:# Tier-A（5 persona 并行，仅在条件满足时跑）：
.planning/codex_personas/README.md:88:### Tier-A（5-persona 并行）
.planning/codex_personas/README.md:106:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/codex_personas/README.md:110:**Tier-A:** If aggregator detects that all 5 personas produce identical or near-identical finding sets, the pipeline marks the review **invalid** and:
.planning/codex_personas/README.md:127:- Tier-A (5-persona, only fires when copy diff ≥10 AND ≥3 [REWRITE/DELETE]): ~1M tokens / sub-phase. Expected frequency: ~1 in 4-5 sub-phases for E11.
.planning/constitution.md:11:> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 跨-sub-phase 轮换 P1→P5→P1，起点 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/constitution.md:153:- **governance bundle #2 persona tier-trigger (2026-04-25, active):** v2.3 触发条件不动，仅追加 §Codex Persona Pipeline Tier-Trigger 子节。E11-09 PR #13 leading indicator fired (≤2 Codex 轮 APPROVE) → 5-persona 默认软化为 tier-trigger（copy diff ≥10 + ≥3 [REWRITE/DELETE] = 5；否则 1）。预期 Codex token 节约 ~70–80% on persona pipeline。详见 v2.3 §Codex Persona Pipeline Tier-Trigger、RETRO-V61-054 §6。
.planning/constitution.md:254:   - **[REWRITE]** 找不到锚点但功能已规划 → 文案改写为 `planned for <Phase-ID> scope` 或 `coming in <Phase-ID>`，并在 §Surface Inventory 标 `[planned:<Phase-ID>]`。
.planning/constitution.md:255:   - **[DELETE]** 找不到锚点且无规划 → 删除该 claim。
.planning/constitution.md:345:| user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5 (Tier-A，全 P1–P5 并行)** | 全跑 |
.planning/constitution.md:346:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | **`.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` 是 Tier-B 选 persona 的唯一 source of truth。** 默认 = 末行 persona 在 P1→P2→P3→P4→P5→P1 序列中的下一位（新 epic 第一行 = P1 Junior FCS）。Owner 可写入非默认值（如 demo-arc 重 → P3；适航 trace 重 → P4），唯一硬约束：写入值**不得**与上一行 Tier-B persona 相同。每次 Tier-B sub-phase commit 后必须追加一行 `<sub-phase-id>: P? (<reason>)`；新 epic 重置序列起点 = P1 |
.planning/constitution.md:348:**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/constitution.md:357:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/constitution.md:371:**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:56:| 1 | static/<file>:L<n> | "<claim>" | feature-name / field-name / behavior / role-gate / data-source / format-spec / limit / surface-location | src/<file>:L<n> 或 E11-XX | [ANCHORED] / [REWRITE → planned for <Phase-ID>] / [DELETE] |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:62:- **Anchor / Plan-ID**：[ANCHORED] 必填 src 锚点 file:line；[REWRITE] 必填 Plan-ID（如 E11-04 / E12-01）；[DELETE] 留 "—"
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:63:- **状态**（枚举）：[ANCHORED] / [REWRITE → planned for <Phase-ID>] / [DELETE]
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:67:- REWRITE-as-planned: <N2>  ← 写入 commit trailer
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:68:- DELETE: <N3>
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:72:- 表为空或与本期 copy diff 行数明显不匹配 → CHANGES_REQUIRED，不进入逐条 ripgrep
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:116:> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:226:**Rebuttal stage**: 本期作者必须在 commit 前对每条 user-facing copy claim 执行 grep 回 src/ 的 sweep，结果登记到 §1.5 Surface Inventory，三选一处置（ANCHORED / REWRITE-as-planned / DELETE）。E11-02 4 轮 Codex round-trip（详 RETRO-V61-054）证明：缺这道反射弧时，Codex 会逐条 ripgrep 在 review 阶段揭穿，付出 4 轮代价；做完反射弧后 Codex 只需抽查 inventory 1-3 行真实性即可一轮 APPROVE。结论：每个含 user-facing copy 的子 phase 必填 §Surface Inventory，不能跳过。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:242:| Codex persona pipeline cost — Tier-A ≈ 5 × 10min ≈ 1h CPU；Tier-B ≈ 10min CPU（governance bundle #2 后默认 Tier-B） | Low | 后台跑（已有先例），Tier-A 时 5 并发；persona 失败 retry 1 次后转 manual review |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:256:   - **Tier-A only:** 必须 ≥1 finding NOT covered by other 4 personas（within-PR uniqueness 反模式同质化）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:261:- **Tier-A**: Claude Code 汇总 5 份 verdict 进 `E11-04-PERSONA-REVIEW-RESULTS.md`（aggregator 模式）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:264:- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一（Tier-A 跨 5/5；Tier-B 该 1/1）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:304:| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:344:> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。

exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	2026-04-26T03:33:09.836228Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
     2	2026-04-26T03:33:09.836280Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
     3	Reading additional input from stdin...
     4	OpenAI Codex v0.118.0 (research preview)
     5	--------
     6	workdir: /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
     7	model: gpt-5.4
     8	provider: openai
     9	approval: never
    10	sandbox: danger-full-access
    11	reasoning effort: xhigh
    12	reasoning summaries: none
    13	session id: 019dc7d9-244d-7ac3-85a5-de6c17609841
    14	--------
    15	user
    16	You are Codex GPT-5.4 acting as **Persona P2 — Senior FCS Engineer** (Tier-B single-persona pipeline, E11-15d sub-phase, **R3 re-review**).
    17	
    18	# Context — E11-15d R3: closure of P2 R2 IMPORTANT + NIT
    19	
    20	**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
    21	**Branch:** `feat/e11-15d-approval-flow-polish-20260426`
    22	**PR:** #29
    23	**Worktree HEAD:** `9d6c85d` (R3 commit on top of R2 `66c7eab`)
    24	**R1 review:** `.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md`
    25	**R2 review:** `.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md`
    26	
    27	## Your R2 findings (for reference)
    28	
    29	You returned **CHANGES_REQUIRED** with:
    30	
    31	- **IMPORTANT** — `tests/test_workbench_approval_flow_polish.py:1`: R2 doesn't fully close the R1 doc-honesty issue. The module header still says this slice "Closes the last English-only surface," while the new guard at `:176` only scanned `E11-15d-SURFACE-INVENTORY.md` for two literal phrases. Same overclaim still shipped in-branch; guard too narrow.
    32	- **NIT** — `E11-15d-SURFACE-INVENTORY.md:86`, `workbench.html` lines 42/48/65/71/77/83/87/209/213/215/278/298/318/301/302: remaining-list still partial. `Manual (advisory)`, system options, state-of-world labels, trust-banner body, boot placeholders, reference-packet block all still English/English-first.
    33	
    34	## What R3 changes (doc-only, no production code touched)
    35	
    36	### IMPORTANT closure — fix test docstring + broaden guard scope
    37	
    38	`tests/test_workbench_approval_flow_polish.py`:
    39	- Module docstring rewritten — removed "Closes the last English-only surface", added P2 R2 IMPORTANT closure note, expanded out-of-scope list to include all surfaces P2 enumerated.
    40	- Guard test renamed `test_e11_15d_artifacts_do_not_overclaim_closure` (was `_surface_inventory_does_not_overclaim_closure`).
    41	- Guard now scans **3 artifacts**: SURFACE-INVENTORY, PERSONA-ROTATION-STATE, AND this test file itself (self-scan is the new safety net).
    42	- Exemption rule simplified: any line with backtick or double-quote = literal reference; bare unquoted mention = fresh assertion = fail. Tighter and clearer than the previous specific-keyword exemption.
    43	
    44	### NIT closure — expand SURFACE-INVENTORY remaining-list
    45	
    46	`E11-15d-SURFACE-INVENTORY.md`:
    47	- Marked the remaining-list as **non-exhaustive** explicitly.
    48	- Added the 8 additional surfaces P2 enumerated: `Manual (advisory)`, system options, state-of-world labels, trust-banner body, boot placeholders, reference-packet block.
    49	- Added a `grep -nE` template so future maintainers can enumerate the long-tail.
    50	- Updated E11-15e estimate from "7+ REWRITE" to "15+ REWRITE → Tier-A".
    51	
    52	## Files in scope (R3 delta)
    53	
    54	- `tests/test_workbench_approval_flow_polish.py` — docstring rewrite + guard rename + scope broadening + exemption simplification
    55	- `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md` — remaining-list expansion + grep template
    56	
    57	## Your specific lens (P2 Senior FCS Engineer, R3)
    58	
    59	Focus on:
    60	- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
    61	  - Confirm zero hits OUTSIDE quoted/backticked/blockquote contexts in any of the three.
    62	- **Is the new guard scope right?** It scans 3 files now. Does it catch the original fault class (overclaim drift in any of the planning artifacts), without false-positives that would block legitimate historical-correction notes?
    63	- **Is the exemption rule sound?** "Any line with `` ` `` or `"`" is a permissive heuristic. A future maintainer could write `It claims "last English-only surface" is achieved` (which has `"`) and the guard would falsely exempt it. Trade-off acceptable for a single doc-honesty NIT, OR should the guard be stricter (e.g., require the phrase to be DIRECTLY adjacent to the quote/backtick)?
    64	- **Is the remaining-list now adequate?** I added the 8 surfaces from your R2 NIT enumeration plus a grep template. Anything else `/workbench` has that's English-first that I still missed?
    65	- **Production code unchanged**: `git diff main..9d6c85d src/well_harness/static/workbench.html` should show only the same 6-string flip from R1. Confirm no scope creep.
    66	- **Approval-flow strings still correct**: spot-check 6 R1 strings (待审 · Pending, 通过 · Accept, 驳回 · Reject, 通过提案, 驳回提案, 已提交的标注提案 ...) still present.
    67	
    68	## Verification status
    69	
    70	- 1154 / 1154 default pytest pass (26 in `test_workbench_approval_flow_polish.py`)
    71	- Truth-engine red line preserved: `git diff --name-only main..9d6c85d` shows only `static/workbench.html` (R1 6 strings only), `tests/test_workbench_approval_flow_polish.py`, and `.planning/`
    72	- Self-scan validates: the guard's own self-reference inside the test file's docstring is correctly exempted (because docstring text wraps the phrases in `"..."` or `` `...` `` literals)
    73	
    74	## Verdict format
    75	
    76	Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.
    77	
    78	Each finding: BLOCKER / IMPORTANT / NIT / INFO with file:line citation. Out-of-scope items → NIT/INFO only.
    79	
    80	Live-probe at least one path. Cite the probe.
    81	
    82	Truth-engine red line: confirm `git diff --name-only main..9d6c85d` shows no changes to production code outside `src/well_harness/static/workbench.html` (which carries only the same 6-string R1 flip).
    83	
    84	Sign as: **P2 — Senior FCS Engineer (Tier-B, E11-15d R3)**
    85	2026-04-26T03:33:14.445103Z ERROR rmcp::transport::worker: worker quit with fatal: Transport channel closed, when Client(Reqwest(reqwest::Error { kind: Decode, source: Error("data did not match any variant of untagged enum JsonRpcMessage", line: 0, column: 0) }))
    86	ERROR: Reconnecting... 2/5
    87	ERROR: Reconnecting... 3/5
    88	ERROR: Reconnecting... 4/5
    89	ERROR: Reconnecting... 5/5
    90	ERROR: Reconnecting... 1/5
    91	ERROR: Reconnecting... 2/5
    92	ERROR: Reconnecting... 3/5
    93	ERROR: Reconnecting... 4/5
    94	ERROR: Reconnecting... 5/5
    95	ERROR: Token data is not available.
    96	ERROR: Token data is not available.

 succeeded in 0ms:
     1	2026-04-26T03:16:08.785864Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
     2	2026-04-26T03:16:08.785949Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
     3	Reading additional input from stdin...
     4	OpenAI Codex v0.118.0 (research preview)
     5	--------
     6	workdir: /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
     7	model: gpt-5.4
     8	provider: openai
     9	approval: never
    10	sandbox: danger-full-access
    11	reasoning effort: xhigh
    12	reasoning summaries: none
    13	session id: 019dc7c9-8fd2-7341-8522-67484e5eb9a6
    14	--------
    15	user
    16	You are Codex GPT-5.4 acting as **Persona P2 — Senior FCS Engineer** (Tier-B single-persona pipeline, E11-15d sub-phase, **R2 re-review**).
    17	
    18	# Context — E11-15d R2: doc-honesty closure of R1 IMPORTANTs
    19	
    20	**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
    21	**Branch:** `feat/e11-15d-approval-flow-polish-20260426`
    22	**PR:** #29
    23	**Worktree HEAD:** `66c7eab` (R2 commit on top of R1 `288d322`)
    24	**Your R1 review:** `.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md` (verdict CHANGES_REQUIRED)
    25	
    26	## Your R1 findings (for reference)
    27	
    28	You returned **CHANGES_REQUIRED** with these 2 IMPORTANTs:
    29	
    30	> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
    31	>
    32	> **IMPORTANT** — `tests/test_workbench_approval_flow_polish.py:1-15, 61-169`, `workbench.html:111, 143, 173, 219-226`: test coverage matches the six-string approval-center polish, not the stronger page-wide closure claim. It does not catch the existing English-first WOW h3s or the multiline English-only dismiss button, so the current docs/test narrative can report full closure while the page still is not Chinese-first end-to-end.
    33	
    34	You also gave 3 INFOs (translation quality OK, structural integrity OK, data-approval markers preserved).
    35	
    36	## What R2 changes (doc-only, no production code touched)
    37	
    38	### IMPORTANT #1 closure — remove overclaim
    39	
    40	`E11-15d-SURFACE-INVENTORY.md`:
    41	- Header banner now states this is "NOT the final Chinese-first sweep" and explicitly references the P2 R1 IMPORTANT.
    42	- Replaced "Closure summary" section with "Workbench Chinese-first thread progress (NOT closure)" + new explicit "English-only surfaces still remaining" section listing the 4 strings you found (with their existing test-lock locations) + WOW starter h3s + topbar chip labels. Deferred to future E11-15e Tier-A bundle.
    43	
    44	`PERSONA-ROTATION-STATE.md` line 24: rewrote E11-15d entry to remove "Closes the last English-only surface" + "uniformly Chinese-first"; added "P2 R1 IMPORTANT closure" note + same deferred-to-E11-15e list.
    45	
    46	### IMPORTANT #2 closure — overclaim guard test
    47	
    48	`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
    49	
    50	Note: the guard does NOT lock the actual remaining English-only strings (those are deferred to E11-15e); it specifically prevents the closure-claim drift you flagged.
    51	
    52	## Files in scope (R2 delta)
    53	
    54	- `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md` — overclaim removed; deferred list added
    55	- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — entry rewritten
    56	- `tests/test_workbench_approval_flow_polish.py` — +1 guard test (now 26 total, was 25)
    57	
    58	## Your specific lens (P2 Senior FCS Engineer, R2)
    59	
    60	Focus on:
    61	- **Did R2 actually close the overclaim?** Re-grep the inventory + rotation-state for `last English-only surface` / `uniformly Chinese-first` outside the leading blockquote and confirm zero hits.
    62	- **Does the deferred list match what you actually found?** I listed 4 strings explicitly + mentioned WOW h3s + topbar chip labels. Anything else /workbench has that's English-first that I missed?
    63	- **Is the guard test sufficient?** It only catches reintroduction of those 2 specific phrases. Other overclaim phrasings (e.g., "the entire workbench Chinese-first work is done", "no English remains") would slip past. Acceptable trade-off for narrow IMPORTANT closure, OR should the guard be broader?
    64	- **Production code unchanged**: confirm `git diff main..66c7eab src/well_harness/static/workbench.html` shows EXACTLY the same 6-string flip as in R1 (no scope creep).
    65	- **Approval-flow strings still correct**: spot-check the 6 R1 strings are still present (待审 · Pending, 通过 · Accept, 驳回 · Reject, 通过提案, 驳回提案, 已提交的标注提案 ...).
    66	
    67	## Verification status
    68	
    69	- 1154 / 1154 default pytest pass (26 in `test_workbench_approval_flow_polish.py`, +1 R2 guard)
    70	- Truth-engine red line preserved: `git diff --name-only main..66c7eab` shows only `static/workbench.html` (R1 strings only), `tests/test_workbench_approval_flow_polish.py`, and `.planning/`
    71	- E11-10 tooling: `python3 tools/codex_persona_dispatch.py collect E11-15d P2` correctly returned `verdict=CHANGES_REQUIRED, IMPORTANT=2, tier_b_acceptance=false` against your R1 output, validating the parser
    72	
    73	## Out of scope (deferred to E11-15e)
    74	
    75	- Bilingualization of `Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`
    76	- Direction flip of WOW starter h3s (`Causal Chain · 因果链走读` style)
    77	- Topbar chip labels (`Identity` / `Ticket` / `Feedback Mode` / `System`)
    78	
    79	These are explicitly enumerated in the SURFACE-INVENTORY now.
    80	
    81	## Verdict format
    82	
    83	Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.
    84	
    85	Each finding: BLOCKER / IMPORTANT / NIT / INFO with file:line citation. Out-of-scope items → NIT/INFO only.
    86	
    87	Live-probe at least one path. Cite the probe.
    88	
    89	Truth-engine red line: confirm `git diff --name-only main..66c7eab` shows no changes to production code outside `src/well_harness/static/workbench.html` (which carries only the same 6-string R1 flip).
    90	
    91	Sign as: **P2 — Senior FCS Engineer (Tier-B, E11-15d R2)**
    92	codex
    93	Using `superpowers:using-superpowers` for startup discipline and the repo memory quick-pass because this is a non-trivial LogicMVP review. I’m going to recover the relevant project context, inspect the R2 delta, and then verify the branch claims against the actual files and a live `/workbench` probe.
    94	exec
    95	/bin/zsh -lc 'rg -n "LogicMVP|ai-fantui-logicmvp|E11-15d|approval flow|workbench" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
    96	exec
    97	/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.codex/plugins/cache/openai-curated/superpowers/421657af0e7e94573f3a5f2c51091df43668da94/skills/using-superpowers/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
    98	 succeeded in 0ms:
    99	---
   100	name: using-superpowers
   101	description: Use when starting any conversation - establishes how to find and use skills, requiring Skill tool invocation before ANY response including clarifying questions
   102	---
   103	
   104	<SUBAGENT-STOP>
   105	If you were dispatched as a subagent to execute a specific task, skip this skill.
   106	</SUBAGENT-STOP>
   107	
   108	<EXTREMELY-IMPORTANT>
   109	If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.
   110	
   111	IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.
   112	
   113	This is not negotiable. This is not optional. You cannot rationalize your way out of this.
   114	</EXTREMELY-IMPORTANT>
   115	
   116	## Instruction Priority
   117	
   118	Superpowers skills override default system prompt behavior, but **user instructions always take precedence**:
   119	
   120	1. **User's explicit instructions** (CLAUDE.md, GEMINI.md, AGENTS.md, direct requests) — highest priority

exec
/bin/zsh -lc "nl -ba tests/test_workbench_approval_flow_polish.py | sed -n '1,240p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""E11-15d — approval-flow polish: bilingualize 3 lane h3s + 2 lane buttons + 1 body copy.
     2	
     3	Bilingualizes the Approval Center lane labels + buttons + pending-lane
     4	body copy (6 strings only). Functional approval-flow strings are now
     5	`<中文> · <English>`, preserving English suffixes for any downstream
     6	substring locks (none currently exist in tests).
     7	
     8	This is one slice in a multi-sub-phase Chinese-first thread; it does
     9	NOT finish the workbench Chinese-first work. P2 R2 IMPORTANT closure:
    10	earlier docstring overclaimed "Closes the last English-only surface" —
    11	corrected. See E11-15d-SURFACE-INVENTORY.md for the (non-exhaustive)
    12	list of English-only surfaces still remaining on /workbench.
    13	
    14	Out of scope:
    15	- API remediation message in demo_server.py:743 — backend contract
    16	  (locked by tests/test_lever_snapshot_manual_override_guard.py:151).
    17	- Approval Center entry button + Kogami-only caption (already
    18	  bilingualized by E11-15b PR #25).
    19	- approval-center-title h2 (already bilingualized by E11-15b PR #25).
    20	- Trust-banner dismiss / authority headline / inbox placeholder /
    21	  pending-signoff strong / WOW h3s / topbar chip labels / state-of-world
    22	  labels / system options / `Manual (advisory)` / boot placeholders /
    23	  reference-packet block — deferred to future E11-15e Tier-A bundle.
    24	"""
    25	
    26	from __future__ import annotations
    27	
    28	import http.client
    29	import threading
    30	from http.server import ThreadingHTTPServer
    31	from pathlib import Path
    32	
    33	import pytest
    34	
    35	from well_harness.demo_server import DemoRequestHandler
    36	
    37	
    38	REPO_ROOT = Path(__file__).resolve().parents[1]
    39	STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
    40	
    41	
    42	def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    43	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    44	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    45	    thread.start()
    46	    return server, thread
    47	
    48	
    49	def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    50	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    51	    connection.request("GET", path)
    52	    response = connection.getresponse()
    53	    return response.status, response.read().decode("utf-8")
    54	
    55	
    56	@pytest.fixture
    57	def server():
    58	    s, t = _start_demo_server()
    59	    try:
    60	        yield s
    61	    finally:
    62	        s.shutdown()
    63	        s.server_close()
    64	        t.join(timeout=2)
    65	
    66	
    67	# ─── 1. New bilingual strings POSITIVELY locked ──────────────────────
    68	
    69	
    70	@pytest.mark.parametrize(
    71	    "bilingual",
    72	    [
    73	        "<h3>待审 · Pending</h3>",
    74	        "<h3>通过 · Accept</h3>",
    75	        "<h3>驳回 · Reject</h3>",
    76	        "通过提案 · Accept Proposal",
    77	        "驳回提案 · Reject Proposal",
    78	        "已提交的标注提案在被通过或驳回前在此排队 · Submitted annotation proposals wait here before acceptance or rejection.",
    79	    ],
    80	)
    81	def test_workbench_html_carries_bilingual_approval_flow_string(bilingual: str) -> None:
    82	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    83	    assert bilingual in html, f"missing bilingual approval-flow string: {bilingual}"
    84	
    85	
    86	# ─── 2. Stale English-only strings are gone ──────────────────────────
    87	
    88	
    89	@pytest.mark.parametrize(
    90	    "stale",
    91	    [
    92	        "<h3>Pending</h3>",
    93	        "<h3>Accept</h3>",
    94	        "<h3>Reject</h3>",
    95	        ">Accept Proposal<",
    96	        ">Reject Proposal<",
    97	    ],
    98	)
    99	def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
   100	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   101	    assert stale not in html, f"stale English-only approval-flow string still present: {stale}"
   102	
   103	
   104	# ─── 3. English suffixes preserved for future substring locks ────────
   105	
   106	
   107	@pytest.mark.parametrize(
   108	    "preserved_english_suffix",
   109	    [
   110	        "Pending</h3>",
   111	        "Accept</h3>",
   112	        "Reject</h3>",
   113	        "Accept Proposal</button>",
   114	        "Reject Proposal</button>",
   115	        "before acceptance or rejection.",  # tail of the body copy
   116	    ],
   117	)
   118	def test_e11_15d_preserves_english_suffix(preserved_english_suffix: str) -> None:
   119	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   120	    assert preserved_english_suffix in html, (
   121	        f"E11-15d broke English suffix invariant: {preserved_english_suffix}"
   122	    )
   123	
   124	
   125	# ─── 4. Structural anchors preserved ─────────────────────────────────
   126	
   127	
   128	@pytest.mark.parametrize(
   129	    "anchor",
   130	    [
   131	        'data-approval-lane="pending"',
   132	        'data-approval-lane="accept"',
   133	        'data-approval-lane="reject"',
   134	        'data-approval-action="accept"',
   135	        'data-approval-action="reject"',
   136	        'class="workbench-approval-grid"',
   137	    ],
   138	)
   139	def test_e11_15d_preserves_structural_anchors(anchor: str) -> None:
   140	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   141	    assert anchor in html, f"E11-15d broke structural anchor: {anchor}"
   142	
   143	
   144	# ─── 5. Live-served route reflects the polish ────────────────────────
   145	
   146	
   147	def test_workbench_route_serves_bilingual_approval_flow(server) -> None:
   148	    status, html = _get(server, "/workbench")
   149	    assert status == 200
   150	    assert "待审 · Pending" in html
   151	    assert "通过 · Accept" in html
   152	    assert "驳回 · Reject" in html
   153	    assert "通过提案 · Accept Proposal" in html
   154	    assert "驳回提案 · Reject Proposal" in html
   155	    assert "已提交的标注提案在被通过或驳回前在此排队" in html
   156	
   157	
   158	# ─── 6. Truth-engine red line — API remediation untouched ────────────
   159	
   160	
   161	def test_e11_15d_does_not_touch_api_remediation_message() -> None:
   162	    """The 409 remediation message is API contract, not display copy."""
   163	    repo_root = Path(__file__).resolve().parents[1]
   164	    demo_server = (repo_root / "src" / "well_harness" / "demo_server.py").read_text(
   165	        encoding="utf-8"
   166	    )
   167	    assert (
   168	        "Acquire sign-off via Approval Center, or switch to auto_scrubber."
   169	        in demo_server
   170	    )
   171	    # Approval-flow Chinese strings must NOT leak into backend
   172	    new_strings = [
   173	        "待审", "通过 · Accept", "驳回 · Reject",
   174	        "通过提案", "驳回提案", "已提交的标注提案",
   175	    ]
   176	    for new_string in new_strings:
   177	        assert new_string not in demo_server, (
   178	            f"E11-15d Chinese {new_string!r} unexpectedly leaked into demo_server.py"
   179	        )
   180	
   181	
   182	# ─── 7. P2 R1 IMPORTANT closure: surface inventory honesty guard ─────
   183	
   184	
   185	def test_e11_15d_artifacts_do_not_overclaim_closure() -> None:
   186	    """P2 R1 + R2 IMPORTANT closure: earlier drafts of the E11-15d
   187	    SURFACE-INVENTORY, the PERSONA-ROTATION-STATE entry, and this test
   188	    module's docstring all claimed `last English-only surface` and/or
   189	    `uniformly Chinese-first`. P2 verified `/workbench` still has many
   190	    English-only surfaces outside this slice (`Hide for session`,
   191	    `Truth Engine — Read Only`, `No proposals submitted yet.`,
   192	    `Pending Kogami sign-off`, WOW h3s, topbar chips, state-of-world
   193	    labels, etc.). All three artifacts were corrected to defer those
   194	    to E11-15e. This guard scans ALL three artifacts to prevent the
   195	    overclaim from being reintroduced silently in any of them.
   196	    """
   197	    repo_root = Path(__file__).resolve().parents[1]
   198	    artifacts = [
   199	        repo_root
   200	        / ".planning"
   201	        / "phases"
   202	        / "E11-workbench-engineer-first-ux"
   203	        / "E11-15d-SURFACE-INVENTORY.md",
   204	        repo_root
   205	        / ".planning"
   206	        / "phases"
   207	        / "E11-workbench-engineer-first-ux"
   208	        / "PERSONA-ROTATION-STATE.md",
   209	        # Self-scan: this test file's own docstring header is included.
   210	        Path(__file__),
   211	    ]
   212	    forbidden_overclaims = [
   213	        "last English-only surface",
   214	        "uniformly Chinese-first",
   215	    ]
   216	    for artifact in artifacts:
   217	        text = artifact.read_text(encoding="utf-8")
   218	        for phrase in forbidden_overclaims:
   219	            # The forbidden phrase is a CLAIM problem, not a literal-mention
   220	            # problem. Exempt lines where the phrase appears inside a quoted
   221	            # context (Markdown blockquote, backticks anywhere on line, or
   222	            # double-quotes anywhere on line) — those are literal references
   223	            # to the phrase, not fresh assertions of the claim. Bare unquoted
   224	            # mentions still fail the guard.
   225	            for line_no, line in enumerate(text.splitlines(), 1):
   226	                if phrase not in line:
   227	                    continue
   228	                if line.lstrip().startswith(">"):
   229	                    continue
   230	                # If the line carries any quote or backtick, the phrase is
   231	                # most likely being referenced as a literal historical note,
   232	                # not asserted as a fresh claim.
   233	                if "`" in line or '"' in line:
   234	                    continue
   235	                raise AssertionError(
   236	                    f"{artifact.name}:{line_no} contains forbidden overclaim "
   237	                    f"phrase {phrase!r}: {line!r}"
   238	                )

codex
我现在补实证：跑 E11-15d honesty guard 和 E11-15e 新 bundle 测试文件，确认我指出的问题不是只靠静态阅读推断。
exec
/bin/zsh -lc 'pytest -q tests/test_workbench_approval_flow_polish.py::test_e11_15d_artifacts_do_not_overclaim_closure tests/test_workbench_e11_15e_chinese_first_bundle.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 742ms:
....................................................................     [100%]
68 passed in 0.57s

exec
/bin/zsh -lc "python3 - <<'PY'
from pathlib import Path
import json, subprocess
repo = Path('.')
artifacts = {
    'E11-15e-SURFACE-INVENTORY.md': repo / '.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md',
    'test_workbench_e11_15e_chinese_first_bundle.py': repo / 'tests/test_workbench_e11_15e_chinese_first_bundle.py',
    '_E11-15e-prompt-shared-context.md': repo / '.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md',
}
body = json.loads(subprocess.check_output(['gh','pr','view','30','--json','body']).decode())['body']
forbidden = ['last English-only surface','uniformly Chinese-first']

def scan(name, text):
    failures=[]
    for phrase in forbidden:
        for i,line in enumerate(text.splitlines(),1):
            if phrase not in line:
                continue
            if line.lstrip().startswith('>'):
                continue
            if '"'`'"' in line or '\"' in line:
                continue
            failures.append((i, phrase, line))
    return failures

for name,path in artifacts.items():
    text = path.read_text(encoding='utf-8')
    print(name, 'PASS' if not scan(name,text) else 'FAIL', scan(name,text))
print('PR_BODY', 'PASS' if not scan('PR_BODY', body) else 'FAIL', scan('PR_BODY', body))
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 862ms:
E11-15e-SURFACE-INVENTORY.md PASS []
test_workbench_e11_15e_chinese_first_bundle.py PASS []
_E11-15e-prompt-shared-context.md PASS []
PR_BODY PASS []

exec
/bin/zsh -lc "rg -n \"SW1|Logic 1|Logic 2|Logic 3|Logic 4|THR LOCK|Control Logic Workbench|Probe & Trace ready|Annotate & Propose ready|Hand Off & Track ready|Scenario actions are staged for the next bundle|Manual \\(advisory\\)|Truth Engine — Read Only|No proposals submitted yet|Pending Kogami sign-off|Hide for session|truth-engine SHA|recent e2e|adversarial|open issues|probe & trace|annotate & propose|hand off & track\" src/well_harness/static/workbench.html src/well_harness/static/workbench.js" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
src/well_harness/static/workbench.html:6:    <title>Control Logic Workbench</title>
src/well_harness/static/workbench.html:18:          <h1>控制逻辑工作台 · Control Logic Workbench</h1>
src/well_harness/static/workbench.html:42:          <strong>手动（仅参考）· Manual (advisory)</strong>
src/well_harness/static/workbench.html:65:          <span class="workbench-sow-label">真值引擎 SHA · truth-engine SHA</span>
src/well_harness/static/workbench.html:71:          <span class="workbench-sow-label">最近 e2e · recent e2e</span>
src/well_harness/static/workbench.html:75:        <span class="workbench-sow-field" data-sow-field="adversarial"
src/well_harness/static/workbench.html:77:          <span class="workbench-sow-label">对抗样本 · adversarial</span>
src/well_harness/static/workbench.html:78:          <span class="workbench-sow-value" data-sow-value="adversarial_label">…</span>
src/well_harness/static/workbench.html:83:          <span class="workbench-sow-label">未关闭问题 · open issues</span>
src/well_harness/static/workbench.html:225:          隐藏（本次会话）· Hide for session
src/well_harness/static/workbench.html:248:          真值引擎 · 只读 · Truth Engine — Read Only
src/well_harness/static/workbench.html:321:            <span>SW1</span>
src/well_harness/static/workbench.html:322:            <span>Logic 1</span>
src/well_harness/static/workbench.html:323:            <span>Logic 2</span>
src/well_harness/static/workbench.html:324:            <span>Logic 3</span>
src/well_harness/static/workbench.html:325:            <span>Logic 4</span>
src/well_harness/static/workbench.html:326:            <span>THR LOCK</span>
src/well_harness/static/workbench.html:337:          <li>暂无已提交提案 · No proposals submitted yet.</li>
src/well_harness/static/workbench.html:363:          <strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>
src/well_harness/static/workbench.js:88:      "Probe & Trace ready. Scenario actions are staged for the next bundle.";
src/well_harness/static/workbench.js:97:      "Annotate & Propose ready. Text-range annotation is staged for the next bundle.";
src/well_harness/static/workbench.js:3788:      label.textContent = mode === "truth_engine" ? "真值引擎 · Truth Engine" : "手动（仅参考）· Manual (advisory)";
src/well_harness/static/workbench.js:3961:// entry button + panel with an explicit "Pending Kogami sign-off"
src/well_harness/static/workbench.js:4045:    writeField("adversarial_label", payload.adversarial_label);

exec
/bin/zsh -lc "python3 - <<'PY'
from pathlib import Path
from collections import Counter
text = Path('.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md').read_text(encoding='utf-8').splitlines()
rows=[]
for line in text:
    if line.startswith('| ') and ' | ' in line and not line.startswith('| # ') and not line.startswith('|---') and not line.startswith('| Metric ') and not line.startswith('|--------') and not line.startswith('| Deferred surface ') and not line.startswith('|------------------') and not line.startswith('| Existing test file ') and not line.startswith('|--------------------') and not line.startswith('| Persona ') and not line.startswith('|---------'):
        rows.append(line)
print('table_rows', len(rows))
for i,r in enumerate(rows,1):
    print(i, r)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "python3 - <<'PY'
from pathlib import Path
import re
p = Path('src/well_harness/static/workbench.html')
lines = p.read_text(encoding='utf-8').splitlines()
# candidate obvious visible English-only text nodes not listed in deferred section by exact snippets
candidates=[]
for i,line in enumerate(lines,1):
    for m in re.finditer(r'>(["'^<>]*[A-Za-z][''^<>]*)<'"', line):
        text=' '.join(m.group(1).split())
        if not text:
            continue
        # skip bilinguals (contains CJK and middot or other CJK chars), obvious ids already deferred, or code path/code tag lines
        if any('\\u4e00' <= ch <= '\\u9fff' for ch in text):
            continue
        if text in {'Kogami / Engineer','WB-E06-SHELL','Thrust Reverser','Landing Gear','Bleed Air Valve','C919 E-TRAS','wow_a','wow_b','wow_c','probe &amp; trace','annotate &amp; propose','hand off &amp; track','Knowledge'}:
            continue
        candidates.append((i,text))
for item in candidates:
    print(f'{item[0]}: {item[1]}')
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
6: Control Logic Workbench
114: /api/lever-snapshot
117: tests/e2e/test_wow_a_causal_chain.py
146: /api/monte-carlo/run
176: /api/diagnosis/run
321: SW1
322: Logic 1
323: Logic 2
324: Logic 3
325: Logic 4
326: THR LOCK

 succeeded in 0ms:
table_rows 51
1 | copy_diff_lines (workbench.html + workbench.js)        | ~38 |
2 | REWRITE rows (display strings rewritten in place)      | **22** |
3 | DELETE rows (English-only string removed without bilingual replacement) | 0 |
4 | ADD rows (new strings introduced for the first time)   | 0 |
5 | 1 | Identity chip label | workbench.html:26 | `<span>Identity</span>` | `<span>身份 · Identity</span>` |
6 | 2 | Ticket chip label | workbench.html:30 | `<span>Ticket</span>` | `<span>工单 · Ticket</span>` |
7 | 3 | Feedback Mode chip label | workbench.html:41 | `<span>Feedback Mode</span>` | `<span>反馈模式 · Feedback Mode</span>` |
8 | 4 | Manual (advisory) chip text (HTML) | workbench.html:42 | `<strong>Manual (advisory)</strong>` | `<strong>手动（仅参考）· Manual (advisory)</strong>` |
9 | 5 | Manual (advisory) chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Manual (advisory)"` literal | `"手动（仅参考）· Manual (advisory)"` |
10 | 6 | Truth Engine chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Truth Engine"` literal | `"真值引擎 · Truth Engine"` |
11 | 7 | System chip label | workbench.html:46 | `<span>System</span>` | `<span>系统 · System</span>` |
12 | 8 | WOW h3 (wow_a) — direction flip | workbench.html:111 | `Causal Chain · 因果链走读` | `因果链走读 · Causal Chain` |
13 | 9 | WOW h3 (wow_b) — direction flip | workbench.html:143 | `Monte Carlo · 1000-trial 可靠性` | `1000-trial 可靠性 · Monte Carlo` |
14 | 10 | WOW h3 (wow_c) — direction flip | workbench.html:173 | `Reverse Diagnose · 反向诊断` | `反向诊断 · Reverse Diagnose` |
15 | 11 | State-of-world label · sha | workbench.html:65 | `truth-engine SHA` | `真值引擎 SHA · truth-engine SHA` |
16 | 12 | State-of-world label · e2e | workbench.html:71 | `recent e2e` | `最近 e2e · recent e2e` |
17 | 13 | State-of-world label · adversarial | workbench.html:77 | `adversarial` | `对抗样本 · adversarial` |
18 | 14 | State-of-world label · open issues | workbench.html:83 | `open issues` | `未关闭问题 · open issues` |
19 | 15 | State-of-world advisory flag | workbench.html:87 | `advisory · not a live truth-engine reading` | `仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading` |
20 | 16 | Trust banner scope `<em>` | workbench.html:209-211 | `<em>What "manual feedback" means here:</em> any value...` | `<em>这里"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入...` |
21 | 17 | Trust banner advisory `<strong>` | workbench.html:213 | `<strong>That mode is advisory.</strong>` | `<strong>该模式仅作参考 · That mode is advisory.</strong>` |
22 | 18 | Trust banner truth-engine `<span>` | workbench.html:215-217 | `Truth engine readings (logic gates L1–L4 ...)` | `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings ...` |
23 | 19 | Trust banner dismiss button | workbench.html:225 | `Hide for session` | `隐藏（本次会话）· Hide for session` |
24 | 20 | Authority banner headline | workbench.html:248 | `Truth Engine — Read Only` | `真值引擎 · 只读 · Truth Engine — Read Only` |
25 | 21 | Pre-hydration boot status (control panel) | workbench.html:278 | `Waiting for probe & trace panel boot.` | `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` |
26 | 22 | Pre-hydration boot status (document panel) | workbench.html:298 | `Waiting for annotate & propose panel boot.` | `等待 annotate & propose 面板启动 · Waiting for annotate & propose panel boot.` |
27 | 23 | Pre-hydration boot status (circuit panel) | workbench.html:318 | `Waiting for hand off & track panel boot.` | `等待 hand off & track 面板启动 · Waiting for hand off & track panel boot.` |
28 | 24 | Reference packet intro `<p>` | workbench.html:301 | `Reference packet, clarification notes...` | `参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, ...` |
29 | 25 | Annotation inbox empty state | workbench.html:337 | `<li>No proposals submitted yet.</li>` | `<li>暂无已提交提案 · No proposals submitted yet.</li>` |
30 | 26 | Pending sign-off `<strong>` | workbench.html:363 | `<strong>Pending Kogami sign-off</strong>` | `<strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>` |
31 | `<option>` system values (`Thrust Reverser`, `Landing Gear`, `Bleed Air Valve`, `C919 E-TRAS`) | Domain proper nouns coupled to value-attribute IDs and the multi-system adapter dispatch in `tests/test_p19_api_multisystem.py`. Bilingualizing the option text would require coordinated changes to value-id parsing, locale-mapping, and the adapter contract. | workbench.html:48-51 |
32 | Post-hydration JS boot status strings (`Probe & Trace ready. Scenario actions are staged for the next bundle.` × 3) | Locked by `tests/test_workbench_column_rename.py:170-172`; would require workbench.js bilingualization with its own lockstep test contract. **Note:** This is the string users actually see for most of session — the "Waiting for ... panel boot." strings E11-15e bilingualizes are pre-hydration only. Re-tier as Tier-A for a follow-up sub-phase. | workbench.js boot fns |
33 | `<pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>` | Visual phase-arrow diagram, not English copy. Would require a Chinese arrow notation decision (e.g. `承接 → 澄清 → 回放 → 诊断 → 知识`); deferred to UX/copy decision. | workbench.html:302 |
34 | `data-wow-id="wow_a"` attribute strings + `data-wow-action="run"` | Internal data-* attributes, not user-visible — out of bilingualization scope by design. | workbench.html:104-194 |
35 | `wow_a/b/c` tag spans (`<span class="workbench-wow-tag">wow_a</span>`) | Card identifier sigil, not display copy; these literally name the API endpoint group. | workbench.html:110/142/172 |
36 | Eyebrow `probe & trace` / `annotate & propose` / `hand off & track` (lowercase column eyebrows) | These are paired with the bilingual `<h2>` titles E11-15c shipped (e.g. `<h2>探针与追踪 · Probe & Trace</h2>`). Eyebrows are intentionally English-only for the column-key tag pattern; if revisited, would need its own constitutional pass. | workbench.html:274/294/314 |
37 | `WB-E06-SHELL` ticket id, `Kogami / Engineer` identity | Identifiers/proper nouns, not display copy. | workbench.html:27/31 |
38 | `test_workbench_trust_affordance.py` | ✅ no change | All 5 substring locks (`Manual (advisory)`, `Truth engine readings`, `Hide for session`, `What "manual feedback" means here`, `That mode is advisory.`) are preserved as English suffixes. |
39 | `test_workbench_authority_banner.py` | ✅ no change | `Truth Engine — Read Only` preserved as suffix. |
40 | `test_workbench_role_affordance.py` | ✅ no change | `Pending Kogami sign-off` preserved as suffix. |
41 | `test_workbench_column_rename.py` | ✅ no change | Pre-hydration `Waiting for ... panel boot.` substrings preserved as suffixes; post-hydration JS strings unchanged (out of scope). |
42 | `test_workbench_state_of_world_bar.py` | ✅ no change | `advisory · not a live truth-engine reading` preserved as suffix. |
43 | `test_workbench_chinese_direction_consistency.py` | ✅ no change | E11-15c column h2 invariant unaffected (no h2 changes). |
44 | `test_workbench_chinese_h2_button_sweep.py` | ✅ no change | h2/button sweep targets are already-bilingual surfaces. |
45 | `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
46 | `test_workbench_e11_15e_chinese_first_bundle.py` (new) | ✅ added | 67 tests — positive bilingual locks, stale-English negative guards, English-suffix preservation locks, structural anchors, JS lockstep, live-served route, truth-engine red-line guard. |
47 | P1 | Engineer-task-flow regression |
48 | P2 | Surface-inventory honesty + closure-claim guards |
49 | P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
50 | P4 | Lockstep test contract preservation (no churn on existing locks) |
51 | P5 | Truth-engine red-line + JS-HTML lockstep |

exec
/bin/zsh -lc "nl -ba .planning/codex_personas/README.md | sed -n '112,124p' && printf '\\n---\\n' && nl -ba .planning/constitution.md | sed -n '340,360p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   112	2. Triggers re-run with sharpened persona contexts
   113	3. If two consecutive re-runs degenerate, escalates to Kogami for manual persona spec rework
   114	
   115	**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
   116	1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
   117	2. **v2.3 UI-COPY-PROBE §Surface Inventory** — grep-anchored claims act as the structural evidence layer that compensates for losing 4 perspectives.
   118	3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
   119	
   120	## Cost / latency baseline (recorded for retro)
   121	
   122	**Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
   123	- PR #5 R1 single Codex review: ~10min wall, ~187k tokens.
   124	- E11-01 baseline 5-persona run: ~10min wall (parallel), ~1M tokens (5 × ~200k).

---
   340	
   341	**新规则（替换"每个 user-facing UI 子 phase 默认跑全 5"）：**
   342	
   343	| 条件 | persona 数 | 选哪个 |
   344	|---|---|---|
   345	| user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5 (Tier-A，全 P1–P5 并行)** | 全跑 |
   346	| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | **`.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` 是 Tier-B 选 persona 的唯一 source of truth。** 默认 = 末行 persona 在 P1→P2→P3→P4→P5→P1 序列中的下一位（新 epic 第一行 = P1 Junior FCS）。Owner 可写入非默认值（如 demo-arc 重 → P3；适航 trace 重 → P4），唯一硬约束：写入值**不得**与上一行 Tier-B persona 相同。每次 Tier-B sub-phase commit 后必须追加一行 `<sub-phase-id>: P? (<reason>)`；新 epic 重置序列起点 = P1 |
   347	
   348	**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
   349	
   350	```bash
   351	git diff --stat $(git merge-base HEAD main)..HEAD -- \
   352	  'src/well_harness/static/*.html' \
   353	  'src/well_harness/static/*.js' \
   354	  'src/well_harness/static/*.css'
   355	```
   356	
   357	读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
   358	
   359	**例外（仍跑全 5）：**
   360	- 该子 phase 触发 v2.2 EMPIRICAL-CLAIM-PROBE 同时也是 user-facing UI 子 phase（数值+surface 双轨断言，需要全角度审）

exec
/bin/zsh -lc "python3 - <<'PY'
from pathlib import Path
p = Path('tests/test_workbench_e11_15e_chinese_first_bundle.py')
text = p.read_text(encoding='utf-8').splitlines()
vals=[]
in_list=False
for line in text:
    if '\"bilingual\"' in line:
        in_list=True
        continue
    if in_list and line.strip()=='],':
        break
    if in_list and line.strip().startswith(('\"',\"'\",'<')):
        vals.append(line.strip().rstrip(','))
print('count', len(vals))
for i,v in enumerate(vals,1):
    print(i, v)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
count 24
1 "<span>身份 · Identity</span>"
2 "<span>工单 · Ticket</span>"
3 "<span>反馈模式 · Feedback Mode</span>"
4 "<span>系统 · System</span>"
5 "<strong>手动（仅参考）· Manual (advisory)</strong>"
6 '<h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>'
7 '<h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>'
8 '<h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>'
9 "真值引擎 SHA · truth-engine SHA"
10 "最近 e2e · recent e2e"
11 "对抗样本 · adversarial"
12 "未关闭问题 · open issues"
13 "仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading"
14 '这里"手动反馈"的含义 · What "manual feedback" means here:'
15 "该模式仅作参考 · That mode is advisory."
16 "真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings"
17 "隐藏（本次会话）· Hide for session"
18 "真值引擎 · 只读 · Truth Engine — Read Only"
19 "等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot."
20 "等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot."
21 "等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot."
22 "参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes"
23 "暂无已提交提案 · No proposals submitted yet."
24 "等待 Kogami 签字 · Pending Kogami sign-off"

exec
/bin/zsh -lc "python3 - <<'PY'
from pathlib import Path
text = Path('.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md').read_text(encoding='utf-8').splitlines()
section2=[]
for line in text:
    if line.startswith('| 1 |'):
        section2.append(line)
    elif section2 and line.startswith('| '):
        # keep rows until non-numbered row or section end
        parts=line.split('|')
        if len(parts)>2 and parts[1].strip().isdigit():
            section2.append(line)
        else:
            break
print('section2_numbered_rows', len(section2))
for r in section2:
    print(r)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
section2_numbered_rows 26
| 1 | Identity chip label | workbench.html:26 | `<span>Identity</span>` | `<span>身份 · Identity</span>` |
| 2 | Ticket chip label | workbench.html:30 | `<span>Ticket</span>` | `<span>工单 · Ticket</span>` |
| 3 | Feedback Mode chip label | workbench.html:41 | `<span>Feedback Mode</span>` | `<span>反馈模式 · Feedback Mode</span>` |
| 4 | Manual (advisory) chip text (HTML) | workbench.html:42 | `<strong>Manual (advisory)</strong>` | `<strong>手动（仅参考）· Manual (advisory)</strong>` |
| 5 | Manual (advisory) chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Manual (advisory)"` literal | `"手动（仅参考）· Manual (advisory)"` |
| 6 | Truth Engine chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Truth Engine"` literal | `"真值引擎 · Truth Engine"` |
| 7 | System chip label | workbench.html:46 | `<span>System</span>` | `<span>系统 · System</span>` |
| 8 | WOW h3 (wow_a) — direction flip | workbench.html:111 | `Causal Chain · 因果链走读` | `因果链走读 · Causal Chain` |
| 9 | WOW h3 (wow_b) — direction flip | workbench.html:143 | `Monte Carlo · 1000-trial 可靠性` | `1000-trial 可靠性 · Monte Carlo` |
| 10 | WOW h3 (wow_c) — direction flip | workbench.html:173 | `Reverse Diagnose · 反向诊断` | `反向诊断 · Reverse Diagnose` |
| 11 | State-of-world label · sha | workbench.html:65 | `truth-engine SHA` | `真值引擎 SHA · truth-engine SHA` |
| 12 | State-of-world label · e2e | workbench.html:71 | `recent e2e` | `最近 e2e · recent e2e` |
| 13 | State-of-world label · adversarial | workbench.html:77 | `adversarial` | `对抗样本 · adversarial` |
| 14 | State-of-world label · open issues | workbench.html:83 | `open issues` | `未关闭问题 · open issues` |
| 15 | State-of-world advisory flag | workbench.html:87 | `advisory · not a live truth-engine reading` | `仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading` |
| 16 | Trust banner scope `<em>` | workbench.html:209-211 | `<em>What "manual feedback" means here:</em> any value...` | `<em>这里"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入...` |
| 17 | Trust banner advisory `<strong>` | workbench.html:213 | `<strong>That mode is advisory.</strong>` | `<strong>该模式仅作参考 · That mode is advisory.</strong>` |
| 18 | Trust banner truth-engine `<span>` | workbench.html:215-217 | `Truth engine readings (logic gates L1–L4 ...)` | `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings ...` |
| 19 | Trust banner dismiss button | workbench.html:225 | `Hide for session` | `隐藏（本次会话）· Hide for session` |
| 20 | Authority banner headline | workbench.html:248 | `Truth Engine — Read Only` | `真值引擎 · 只读 · Truth Engine — Read Only` |
| 21 | Pre-hydration boot status (control panel) | workbench.html:278 | `Waiting for probe & trace panel boot.` | `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` |
| 22 | Pre-hydration boot status (document panel) | workbench.html:298 | `Waiting for annotate & propose panel boot.` | `等待 annotate & propose 面板启动 · Waiting for annotate & propose panel boot.` |
| 23 | Pre-hydration boot status (circuit panel) | workbench.html:318 | `Waiting for hand off & track panel boot.` | `等待 hand off & track 面板启动 · Waiting for hand off & track panel boot.` |
| 24 | Reference packet intro `<p>` | workbench.html:301 | `Reference packet, clarification notes...` | `参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, ...` |
| 25 | Annotation inbox empty state | workbench.html:337 | `<li>No proposals submitted yet.</li>` | `<li>暂无已提交提案 · No proposals submitted yet.</li>` |
| 26 | Pending sign-off `<strong>` | workbench.html:363 | `<strong>Pending Kogami sign-off</strong>` | `<strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>` |

codex
结论已经收敛了：P2 旧清单本身基本都被 E11-15e 覆盖或显式 deferred，overclaim guard 也确实没回潮。现在剩下的是两类文档层问题：Section 3 的 deferred list 仍漏了真实可见的英文表面，以及 Tier/row 计数在 inventory、shared context、test docstring 之间对不齐。
  ✓ Cross-reference E11-15d P2 prior findings against E11-15e Section 2/3 and current diff
  ✓ Audit overclaim language in inventory/tests and compare against E11-15d guard semantics
  ✓ Walk current /workbench surfaces for missing English-only items outside rewrite/deferred lists
  ✓ Recompute Tier-A metrics and persona successor from repo state/tooling
  → Write P2 verdict with severity-tagged findings and precise file:line refs
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '842,862p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   842	# Task Group: AI FANTUI LogicMVP autonomous Notion-synced development
   843	
   844	scope: Continue AI FANTUI LogicMVP automatically from `.planning` and Notion-synced state, keep the control tower current, and use approved/no-review gate state to decide whether to keep moving.
   845	applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s autonomous GSD + Notion workflow, but exact phase numbers and page text are repo-specific.
   846	
   847	## Task 1: Build an isolated Notion hub and harden repo-side sync/timeouts
   848	
   849	### rollout_summary_files
   850	
   851	- rollout_summaries/2026-04-08T15-29-03-VmzV-notion_api_hub_and_p6_sync_timeout_baseline_restore.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/08/rollout-2026-04-08T23-29-03-019d6db6-16ac-7431-9092-63393e7770a3.jsonl, updated_at=2026-04-11T04:03:27+00:00, thread_id=019d6db6-16ac-7431-9092-63393e7770a3, isolated hub and P6 timeout/baseline recovery)
   852	
   853	### keywords
   854	
   855	- AI FANTUI LogicMVP 控制塔, NOTION_API_KEY, gsd_notion_sync.py, prepare-opus-review, writeback timeout, stronger QA baseline, 175 tests OK, 10 demo smoke scenarios pass, 8/8 shared validation checks pass
   856	
   857	## Task 2: Keep advancing automatically when Notion says Approved / 当前无需 Opus 审查
   858	
   859	### rollout_summary_files
   860	
   861	- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, P7 workbench slices synced with dashboard/status/09C/freeze)
   862	- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, P8 runtime-generalization work stayed autonomous through Notion writeback and gate recheck)

codex
CHANGES_REQUIRED

- `IMPORTANT` [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:321), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:6), [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:76): Section 3 is still incomplete. The live `/workbench` HTML still exposes English-only circuit-skeleton labels `SW1`, `Logic 1`, `Logic 2`, `Logic 3`, `Logic 4`, `THR LOCK` at lines 321-326, and the browser-tab title remains `Control Logic Workbench` at line 6. None of these appear in Section 2’s rewrite table or Section 3’s deferred table.  
  Suggested fix: add these surfaces explicitly to Section 3 with rationale, or reclassify them as in-scope and lock them in tests.

- `IMPORTANT` [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:19), [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:64), [_E11-15e-prompt-shared-context.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:6), [test_workbench_e11_15e_chinese_first_bundle.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:3): the Tier/count evidence is not reproducible as written. By constitution, `copy_diff_lines` is insertions+deletions; `git diff --stat main..83d69e4 -- workbench.html workbench.js` yields `28 + 28 = 56`, not `~38`. Section 2 contains 26 numbered rewrite rows, the positive HTML lock list contains 24 entries, and the new test docstring still says `17`. Tier-A still fires because `56 >= 10` and REWRITE is well above `3`, but the published `22` / `~38` math is internally inconsistent.  
  Suggested fix: normalize one canonical counting scheme across PR body, shared context, SURFACE-INVENTORY, and the new test docstring, and spell out dedup arithmetic that actually lands on the published number.

All items from my E11-15d R1/R2 lists are otherwise accounted for: `Manual (advisory)`, system options, state-of-world labels, trust-banner body, boot placeholders, reference packet, `Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`, WOW h3s, and topbar chips are now either rewritten in Section 2 or explicitly deferred in Section 3. I did not find one of those earlier P2 items falling through.

Overclaim drift is clean. Extending the E11-15d heuristic to PR #30 body, [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:72), [_E11-15e-prompt-shared-context.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:35), and [test_workbench_e11_15e_chinese_first_bundle.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:1) produced no fresh `last English-only surface` / `uniformly Chinese-first` claims. `pytest -q tests/test_workbench_approval_flow_polish.py::test_e11_15d_artifacts_do_not_overclaim_closure tests/test_workbench_e11_15e_chinese_first_bundle.py` passed with `68 passed`.

Persona succession is correct: `python3 tools/codex_persona_dispatch.py next-persona` returned `P3`, matching [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:25) and the canonical P1→P2→P3→P4→P5→P1 rule in [README.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/codex_personas/README.md:116).


tokens used
189,497
CHANGES_REQUIRED

- `IMPORTANT` [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:321), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:6), [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:76): Section 3 is still incomplete. The live `/workbench` HTML still exposes English-only circuit-skeleton labels `SW1`, `Logic 1`, `Logic 2`, `Logic 3`, `Logic 4`, `THR LOCK` at lines 321-326, and the browser-tab title remains `Control Logic Workbench` at line 6. None of these appear in Section 2’s rewrite table or Section 3’s deferred table.  
  Suggested fix: add these surfaces explicitly to Section 3 with rationale, or reclassify them as in-scope and lock them in tests.

- `IMPORTANT` [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:19), [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:64), [_E11-15e-prompt-shared-context.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:6), [test_workbench_e11_15e_chinese_first_bundle.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:3): the Tier/count evidence is not reproducible as written. By constitution, `copy_diff_lines` is insertions+deletions; `git diff --stat main..83d69e4 -- workbench.html workbench.js` yields `28 + 28 = 56`, not `~38`. Section 2 contains 26 numbered rewrite rows, the positive HTML lock list contains 24 entries, and the new test docstring still says `17`. Tier-A still fires because `56 >= 10` and REWRITE is well above `3`, but the published `22` / `~38` math is internally inconsistent.  
  Suggested fix: normalize one canonical counting scheme across PR body, shared context, SURFACE-INVENTORY, and the new test docstring, and spell out dedup arithmetic that actually lands on the published number.

All items from my E11-15d R1/R2 lists are otherwise accounted for: `Manual (advisory)`, system options, state-of-world labels, trust-banner body, boot placeholders, reference packet, `Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`, WOW h3s, and topbar chips are now either rewritten in Section 2 or explicitly deferred in Section 3. I did not find one of those earlier P2 items falling through.

Overclaim drift is clean. Extending the E11-15d heuristic to PR #30 body, [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:72), [_E11-15e-prompt-shared-context.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:35), and [test_workbench_e11_15e_chinese_first_bundle.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:1) produced no fresh `last English-only surface` / `uniformly Chinese-first` claims. `pytest -q tests/test_workbench_approval_flow_polish.py::test_e11_15d_artifacts_do_not_overclaim_closure tests/test_workbench_e11_15e_chinese_first_bundle.py` passed with `68 passed`.

Persona succession is correct: `python3 tools/codex_persona_dispatch.py next-persona` returned `P3`, matching [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:25) and the canonical P1→P2→P3→P4→P5→P1 rule in [README.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/codex_personas/README.md:116).



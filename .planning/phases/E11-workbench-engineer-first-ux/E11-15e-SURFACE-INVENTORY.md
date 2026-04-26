# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY

**Date:** 2026-04-26 (R1 dispatched 2026-04-26, R2 patched same day)
**Status:** R2 in_review (Tier-A, 26 REWRITE rows after R2 expansion → 5-persona re-dispatch)
**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
**Scope:** Bilingualize the user-visible English-only surfaces on `/workbench`
that P2 enumerated during the E11-15d Tier-B review (see
`tests/test_workbench_approval_flow_polish.py:189-194`).

## R2 closure log (2026-04-26)

R1 dispatch: P1 APPROVE_WITH_NITS (3 NITs), P2 incomplete codex output, P3
CHANGES_REQUIRED (3 IMPORTANT + 1 NIT), P4 incomplete codex output, P5
CHANGES_REQUIRED (2 IMPORTANT + 1 NIT). R2 incorporates **all** actionable
findings from P1/P3/P5 in a single patch:

| Finding | Source | R2 fix |
|---------|--------|--------|
| `title="Manual feedback override is advisory…"` English-only | P3 IMPORTANT 1 + P1 NIT 1 | Bilingualized + locked + inventory row #27 added |
| `1000-trial 可靠性 · Monte Carlo` not strict Chinese-first | P3 IMPORTANT 2 | Changed to `1000 次试验可靠性 · Monte Carlo`; row #9 updated |
| Multi-middot inside Chinese half (rows #15, #20) | P3 IMPORTANT 3 | Outer middot reserved for CN/EN split; inner clauses use comma / parentheses |
| Trust banner Chinese awkward calque | P3 NIT + P1 NIT 2 | `这里…` → `此处…`; `仍然是权威` → `仍以真值引擎读数为准`; `不算 manual feedback` → `不属于"手动反馈"` |
| `aria-label`s on dismiss button + trust banner + authority banner English-only | P1 NIT 1 + P3 IMPORTANT 1 | All 3 aria-labels bilingualized; rows #28-#30 added |
| Section 7 guard list missing trust-banner truth-engine sentence + JS truth_engine label | P5 IMPORTANT 1 | Guard list extended to cover both shipped strings |
| Guard doesn't traverse `src/well_harness/adapters/` | P5 IMPORTANT 2 | Guard now walks `adapters/**/*.py` via `rglob`, with sanity-check that ≥1 adapter file is found |

R2 verification: 80/80 new tests pass (was 67 in R1; +13 new locks); 357/357
workbench-suite tests pass; **1234/1234** full suite pass (was 1221 in R1).

## R2 deferred (still legitimate per Section 3 surface-honesty pledge)

- P1 NIT 3: post-hydration JS boot status strings (`Probe & Trace ready. ...` × 3) remain English-only — explicitly deferred per Section 3.
- P3 NIT (full sentence-split of trust-banner English clause): would require restructuring the existing semantic block (`<em>` + `<strong>` + `<span>` triplet). Deferred to a UX/copy decision; the R2 native-phrasing tightening already addresses the worst part of the density complaint.
- P5 NIT (boot-path comment about `installFeedbackModeAffordance` not auto-calling `setFeedbackMode`): no behavioral bug, no fix required.

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
| 9 | WOW h3 (wow_b) — direction flip + R2 strict Chinese-first | workbench.html:143 | `Monte Carlo · 1000-trial 可靠性` | `1000 次试验可靠性 · Monte Carlo` |
| 10 | WOW h3 (wow_c) — direction flip | workbench.html:173 | `Reverse Diagnose · 反向诊断` | `反向诊断 · Reverse Diagnose` |
| 11 | State-of-world label · sha | workbench.html:65 | `truth-engine SHA` | `真值引擎 SHA · truth-engine SHA` |
| 12 | State-of-world label · e2e | workbench.html:71 | `recent e2e` | `最近 e2e · recent e2e` |
| 13 | State-of-world label · adversarial | workbench.html:77 | `adversarial` | `对抗样本 · adversarial` |
| 14 | State-of-world label · open issues | workbench.html:83 | `open issues` | `未关闭问题 · open issues` |
| 15 | State-of-world advisory flag (R2: comma instead of inner middot) | workbench.html:87 | `advisory · not a live truth-engine reading` | `仅参考，非真值引擎实时读数 · advisory · not a live truth-engine reading` |
| 16 | Trust banner scope `<em>` (R2: `此处` + `不属于"手动反馈"`) | workbench.html:209-211 | `<em>What "manual feedback" means here:</em> any value...` | `<em>此处"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入...` |
| 17 | Trust banner advisory `<strong>` | workbench.html:213 | `<strong>That mode is advisory.</strong>` | `<strong>该模式仅作参考 · That mode is advisory.</strong>` |
| 18 | Trust banner truth-engine `<span>` (R2: `仍以真值引擎读数为准`) | workbench.html:215-217 | `Truth engine readings (logic gates L1–L4 ...)` | `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍以真值引擎读数为准 · Truth engine readings ...` |
| 19 | Trust banner dismiss button | workbench.html:225 | `Hide for session` | `隐藏（本次会话）· Hide for session` |
| 20 | Authority banner headline (R2: parentheses instead of inner middot) | workbench.html:248 | `Truth Engine — Read Only` | `真值引擎（只读）· Truth Engine — Read Only` |
| 21 | Pre-hydration boot status (control panel) | workbench.html:278 | `Waiting for probe & trace panel boot.` | `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` |
| 22 | Pre-hydration boot status (document panel) | workbench.html:298 | `Waiting for annotate & propose panel boot.` | `等待 annotate & propose 面板启动 · Waiting for annotate & propose panel boot.` |
| 23 | Pre-hydration boot status (circuit panel) | workbench.html:318 | `Waiting for hand off & track panel boot.` | `等待 hand off & track 面板启动 · Waiting for hand off & track panel boot.` |
| 24 | Reference packet intro `<p>` | workbench.html:301 | `Reference packet, clarification notes...` | `参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, ...` |
| 25 | Annotation inbox empty state | workbench.html:337 | `<li>No proposals submitted yet.</li>` | `<li>暂无已提交提案 · No proposals submitted yet.</li>` |
| 26 | Pending sign-off `<strong>` | workbench.html:363 | `<strong>Pending Kogami sign-off</strong>` | `<strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>` |
| 27 | Feedback-mode chip `title` attribute (R2 P3 IMPORTANT 1 + P1 NIT 1 closure) | workbench.html:39 | `title="Manual feedback override is advisory — truth engine readings remain authoritative."` | `title="手动反馈覆盖仅作参考，仍以真值引擎读数为准 · Manual feedback override is advisory — truth engine readings remain authoritative."` |
| 28 | Trust banner `aria-label` (R2 P1 NIT 1 closure) | workbench.html:204 | `aria-label="Feedback mode trust affordance"` | `aria-label="反馈模式信任说明 · Feedback mode trust affordance"` |
| 29 | Trust dismiss button `aria-label` (R2 P1 NIT 1 closure) | workbench.html:222 | `aria-label="Hide trust banner for this session"` | `aria-label="隐藏本次会话的信任提示横幅 · Hide trust banner for this session"` |
| 30 | Authority banner `aria-label` (R2 P1 NIT 1 closure) | workbench.html:244 | `aria-label="Truth-engine authority contract"` | `aria-label="真值引擎权限契约 · Truth-engine authority contract"` |

(R2 expanded count: 26 REWRITE rows after dedup of #5/#6 with their HTML siblings,
plus 4 R2 accessibility/hover names = **30 row IDs / ~26 distinct surfaces**.
Tier-A trigger remains satisfied; copy_diff_lines now ≈ 50.)

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

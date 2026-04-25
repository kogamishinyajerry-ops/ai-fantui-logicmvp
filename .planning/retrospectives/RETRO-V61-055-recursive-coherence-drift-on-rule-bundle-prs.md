# RETRO-V61-055 · Recursive coherence drift on rule-bundle PRs

> **Date:** 2026-04-25
> **Trigger:** governance bundle #2 (PR #14) ran 6 Codex rounds — well past v6.1 Hard Stop (≥4 rounds = governance failure).
> **Same arc as:** v2.3 UI-COPY-PROBE legislation PR (PR #11, 5 rounds), captured upstream in RETRO-V61-054 §5b/§6.5 as a candidate methodology lesson.
> **Status:** Methodology rule. Adopt for ALL future governance/rule-bundle PRs in this repo.

---

## 1. Pattern recognition

Rule-bundle PRs (governance changes that touch constitution.md + RETRO + at-least-1 phase plan) consistently exhibit a recursive coherence drift loop:

1. R1 catches structural finding (BLOCKER or IMPORTANT)
2. Author rewrites the rule in N spots to fix the structural issue
3. R2 catches that the N rewrites produced N slightly-different paraphrases
4. Author "converges" by editing N spots to be more similar
5. R3 catches that "more similar" still has fragments diverging
6. ... repeat until R5–R6, by which point Codex is finding rule fragments in changelog narratives, RETRO history sections, and README operational mechanisms — places that are NOT structural rule-body but contain rule-shaped sentences

**Two confirmed instances:**
- PR #11 (v2.3 UI-COPY-PROBE birth): 5 rounds. Captured in RETRO-V61-054.
- PR #14 (governance bundle #2): 6 rounds. Captured here.

The actual *legislative output* of both PRs was correct from R1. All 6 (and 5) rounds re-litigated *cross-doc references* to that output, not the output itself.

---

## 2. Root cause

Two compounding factors:

### 2.1 Spec-coherence-as-fractal trap
Codex (gpt-5.4) reviewing for spec coherence finds drift at every zoom level:
- R1 zoom: sections disagree
- R2 zoom: paragraphs in same section disagree
- R3 zoom: sentences in same paragraph disagree
- R4 zoom: clauses within same sentence disagree
- R5 zoom: word choice in synonymous clauses disagree

There is no natural stopping point. Coherence is asymptotic; perfect convergence is a fixed-point that may not be reachable in finite rounds because each rewrite introduces new surface.

### 2.2 Author overpromise compounds with Codex literalism
Author commit messages claim ambitious convergence ("3 spots verbatim identical", "canonical-pointer pattern", "1 canonical + N pointers"). Codex grades against the literal claim. When the claim is achievable only at a deeper purity level than was actually achieved, Codex flags drift on the gap between claimed and delivered.

---

## 3. Methodology rule (ratified by Opus 4.7 strategic review, 2026-04-25)

> **§3 scope** *(Opus Q3 amendment)*: all §3 rules apply only to **doc-only** rule-bundle PRs. Source-code rule-bundle PRs (e.g., new authority gate in `runner.py`) follow standard R4 Opus trigger and v6.1 Hard Stop ≥4. If 同型 loop 在 source-code PR 上首次出现，open a successor RETRO before extending §3.
>
> **Rationale (Opus)**: source code has pytest + executability automatically grounding spec drift; spec coherence drift is a doc-only phenomenon (no compiler). Legislating §3 without explicit scope = over-extension to unobserved scenarios, itself a v2.2 EMPIRICAL-CLAIM-PROBE violation.

### 3.1 Anti-superlative claim rule *(Opus Q2 amendment — replaces prior "allowed-restatement zone" approach)*

The root cause of recursive coherence drift is asymmetric grading: **Codex grades strictly literally against any superlative claim the author writes in commit messages or PR descriptions**. As soon as the author asserts `verbatim identical` or `pure pointers`, Codex treats 100% character equality as a required passing condition; any partial-convergence is flagged as drift.

**Rule**: rule-bundle PR commit messages and PR descriptions are **forbidden** to use superlative coherence claims. The banned phrase list (Chinese + English):

- `verbatim identical` / 字面相等 / 完全一致
- `pure pointers` / 纯指针 / 仅指针
- `1 canonical + N pointers` / 单源 + 全指针
- `zero drift` / 零漂移
- `fractal-clean` / 全层级一致

**Standard substitute template** (use verbatim):

> *"1 canonical source at `<path>`; downstream references may drift in wording but must not contradict canonical."*

This attacks the feedback loop itself — one order of magnitude smaller than enumerating "allowed-restatement zones" per-PR (which itself drifts between PRs and can be reverse-graded by Codex).

### 3.2 R3 Opus consultation trigger for doc-only rule-bundle PRs *(Opus Q1 amendment)*

A PR qualifies as "rule-bundle" iff:

- (a) it modifies ≥1 constitution rule body **AND** (b) adds/rewrites ≥2 cross-doc pointers to that rule, **OR**
- (c) it is explicitly labeled `governance-bundle` in commit subject prefix or PR title

Such PRs trigger automatic Opus 4.7 Notion strategic review consultation at **R3** (普通 PR 仍 R4). Continuing past R3 without Opus input enters known-trap territory.

The objective trigger condition (a∧b ∨ c) prevents the trigger itself from drifting between PRs.

### 3.3 R-budget two-tier cap *(Opus Q4 amendment)*

For doc-only rule-bundle PRs:

- **R3**: §3.2 Opus consultation trigger fires
- **R5**: mandatory `drift-acceptance` declaration in PR body listing every outstanding cross-doc delta Codex flagged (using §3.1 standard template phrasing, no superlatives)
- **R6**: hard cap, binary author choice:
  - (a) rollback to a smaller bundle, OR
  - (b) merge-with-explicit-drift signed by author (PR body must contain the drift-acceptance list)

After 3 doc-only rule-bundle PRs run under this new regime, re-evaluate whether to tighten the hard cap to R5 (currently R6 because PR #14 successfully merged at R6 with drift acceptance — capping below already-observed-successful values would block known viable paths and force authors to split rule-bundles into 2 PRs, doubling drift surface).

### 3.4 (deprecated by §3.1)

The original §3.4 "anti-overpromise commit-message rule" is subsumed by Opus's §3.1 amendment (root-cause fix is the explicit superlative ban + standard template, not a vague anti-overpromise heuristic).

---

## 4. PR #14 specific — what we accepted as drift

Per Path A merge (2026-04-25), PR #14 ships with these R6-flagged drift surfaces NOT fixed (recorded as "drift accepted by design"):

- `constitution.md:11,151` — changelog summary lines mentioning tier-trigger. Drift accepted: changelog by definition summarizes; pure-pointer changelog is uninformative.
- `RETRO-V61-054.md:161-164` (§6.3) — rollback condition body. Drift accepted: rollback rule was authored in RETRO context (the bundle's own retro), and is referenced from constitution.md:359 as canonical. Constitution treats RETRO §6.3 as the rule home for this specific clause.
- `README.md:104-106, 115-118, 127-131` — Output convention upgrade-path mention, Anti-bias safeguard rollback ref, Cost rollback ref. Drift accepted: these are README's owned operational documentation. They contain rule-shaped sentences because they describe the operational view of the rule, not the rule itself.
- `E11-00-PLAN.md:181, 257, 304, 344` — historical / closure / verification table references. Drift accepted: closure tables and verification tables need acceptance criteria phrased operationally, not as pure pointers. Replacing with pointers would make the closure check unverifiable.

**Test of acceptance:** if a future change to constitution.md:343 (the canonical rule) renders any of the above lines false, that's drift. As of 2026-04-25 commit ee602b0, all listed lines remain consistent with constitution.md:343.

---

## 5. Open questions — resolved by Opus 4.7 (2026-04-25)

- **Q1 (codify §3.2 R3-trigger now or wait for 3rd instance?)** → **CODIFY NOW with objective trigger**. Opus rationale: 2 instances same root cause = mechanism generalized; waiting for N=3 is itself recursive-process-bloat (§1's diagnosis self-applied). §3.2 amended with objective (a∧b ∨ c) trigger.
- **Q2 (allowed-restatement zone list itself drift-prone?)** → **AMEND root cause**. Opus reframed: real cause is Codex grading author's superlative claim literally, not "restatement allowed/not". §3.1 replaced with explicit superlative-claim ban + standard-template phrase.
- **Q3 (doc-only scope or source-code too?)** → **CODIFY NOW with explicit doc-only scope**. Opus rationale: source code has pytest/executability auto-grounding spec drift; legislating without scope violates v2.2 EMPIRICAL-CLAIM-PROBE. §3 preamble adds "doc-only only" + RETRO-trigger if pattern observed on source-code PR.
- **Q4 (4-round R-budget cap)** → **AMEND to R3/R5/R6 two-tier**. Opus rationale: 4-cap below already-observed-successful R6 of PR #14 would block known viable path + force PR splits doubling drift surface. §3.3 amended with R3 trigger / R5 declaration / R6 hard cap; re-evaluate to R5 after 3 PRs in new regime.

New open questions (post-Opus):
- **Q5**: After 3 doc-only rule-bundle PRs run under §3.2 R3 trigger + §3.3 R6 cap, is the empirical R5/R6 distribution biased toward R6? If yes, tighten cap to R5 in successor RETRO. (Telemetry: track Codex-rounds-to-merge per rule-bundle PR.)

---

## 6. Provenance

- **Initial diagnosis**: in-session, 2026-04-25, after PR #14 R6 verdict
- **Strategic review**: Opus 4.7 (Notion async session, 2026-04-25) — 4/4 codify/amend (see §3 verbatim Opus rewrites)
- **Status**: methodology rule **ratified**; constitution v2.4 amendment landing in same PR (#15)
- **Supersedes**: RETRO-V61-054 §6.5 candidate marker (now formalized)

---

## 7. Trailer

```
Authored-by: claudecode-opus47 · v6.1 · solo-autonomy
Strategic-reviewer: Opus 4.7 (Notion async, 2026-04-25 ratified)
Status: methodology ratified; pairs with constitution v2.4 amendment
Supersedes: RETRO-V61-054 §6.5 candidate marker
```

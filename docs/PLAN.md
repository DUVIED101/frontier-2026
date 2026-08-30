# Approved plan — Skilled Worker sponsorship verification

This is the recovery point. A session resuming this project needs `CLAUDE.md`, this file,
and `docs/DECISIONS.md` — no chat history. Every MUST rule in `CLAUDE.md` binds all work
described here.

## Status — 2026-08-30, after the final run

The body below is the approved 2026-08-28 plan, unedited. Reality diverged from it in
places; this block records the divergence rather than editing the plan to look
prescient. Reasoning for every item: `docs/DECISIONS.md`.

- **Built as planned:** pipeline A (extract → resolve → rules → verify → render), the
  §5b verification report as a pure renderer, the self-consistency removed experiment
  (rejected by its own numbers, CHANGELOG [5]), the 10-case holdout held untouched
  until the final run, the frozen baseline.
- **Contingencies that fired:** cut-order item 1 — the B-rating sub-check was cut and
  folded into the uncertainty statement exactly as §8 provides; case-28 prices that
  cut and is the one wrong verdict in the final run. Item 2 (the alias layer) was
  provisionally out and restored to scope on Saturday morning — and it shipped as
  **synthetic alias fixtures** (`aliases.json`), not the "cached Companies House name
  lookups" the §5 table describes. No Companies House data exists in this repo; where
  this plan and `docs/DATA.md` disagree about that artifact, DATA.md is correct.
- **Scope the plan did not contain:** a demo CLI (`python -m src.advanced.cli`,
  CHANGELOG [9]); a dirty-tree guard on tagged eval runs; the collision sweep
  (`eval/collision_sweep.py`); two dev cases added from live-input blind spots
  (CHANGELOG [10]/[11]) — so §7's "~30 total" and §8's "full 30" ended at **32 cases
  (22 dev / 10 holdout)**.
- **Where it ended:** final run of record `eval/results/20260830-101148.json` —
  advanced verdict_utility 0.9375 (holdout 1.0), baseline 0.5547, trivial abstention
  0.4844.

## Context

micro1 Agentic Workflows Hackathon (kickoff 16:00 London, Fri 28 Aug 2026; submission
target Sun evening, hard stop Mon 18:00 UTC). The brief prescribes no problem — the
participant chooses it — and scores out of 100: Problem & User Value 15, Agent Solution &
Engineering 30, End-to-End Quality 20, Measured Improvement 15, Reproducibility 15,
Hot Take 5. Required deliverables: complete solution code with an improvement changelog, a
reproduction guide for a clean environment, a video of at most 5 minutes, and
representative trajectories for every agent used. A fair simple baseline (for example, one
direct prompt with basic instructions) must be compared against the final solution on the
same cases.

The chosen domain: **verifying whether a UK job requisition can lead to a Skilled Worker
Certificate of Sponsorship**. The pre-kickoff scaffold (evaluation harness, frozen-baseline
discipline, changelog, trajectories) maps 1:1 onto the deliverables and stays as-is.

**Status: approved 2026-08-28 by the author, with four amendments, all incorporated
below.** (1) Evaluation cases are synthetic fixtures authored from documented real
archetypes — this is the first execution task, before the baseline. (2) The memory
approach is cut at planning. (3) The human-readable verification report is a first-class
deliverable (§5b). (4) Assumptions are confirmed as recorded in the approval record.
Guiding principle from the review, binding throughout: **code decides, the model
extracts — a model is never the last thing between evidence and a verdict.**

---

## 1. Restatement

*(§1 rewritten 2026-08-29 per checkpoint: cost basis corrected from "irreplaceable
applications" to attention under a deadline, and the bottleneck restated as
time-to-a-trustworthy-answer. The verdict-asymmetry design is unchanged; only its
justification is. See the trajectory record.)*

An early-career software engineer already working in the UK needs Skilled Worker
sponsorship to keep working there, and works against a visa deadline in a market where
roles at their level close within 48 hours. Whether a requisition is viable rests on
four independent facts that live in three different places: the hiring **legal entity**
appears on the Home Office sponsor register (published under registered names, while
postings use trading names); that entity's licence covers the **Skilled Worker route**
specifically (a Global Business Mobility-only licence is an intra-company route this
user cannot use); the employer is **willing** to sponsor *this* requisition (holding a
licence and using it are different facts); and the advertised **salary** clears the
applicable floor — £38,300 for SOC 2134 new-entrant per the confirmed rules snapshot.
Any single failed check kills the application, and the checks fail independently. The
application form is the cheap part of getting this wrong. The expensive part is what
follows — screening call, recruiter conversation, technical interview: hours spent
before the sponsorship constraint surfaces, on a process that could never have ended in
an offer. The scarce resource is attention and calendar time under that deadline; every
requisition examined pointlessly is one not examined instead.

What this user does today — the author's actual current process, stated as such — is
paste the requisition into a chat session that already has the register loaded and get
an answer in about a minute. Producing an answer was never the bottleneck; trusting it
is. That one-minute answer is confidently wrong on a large fraction of its definitive
verdicts and cites evidence that does not survive checking, so acting on it means
re-deriving it against the register by hand — which costs more than the answer did. The
honest measure is therefore **time-to-a-trustworthy-answer**: the time until the user
can act, including the time spent verifying — or failing to verify — what the tool
claimed. This is what the Sunday timing measurement captures, per the protocol in §6.

The system takes a requisition (pasted text; URL only in demo mode) plus the public
sponsor register snapshot and returns **SPONSORABLE / NOT SPONSORABLE / UNVERIFIABLE**,
delivered as a plain-English verification report a person reads before spending time on
a role: the evidence behind each of the four checks and an explicit uncertainty
statement. The error costs are asymmetric and — worse — unauditable by the user, and
the metric encodes it: a false SPONSORABLE sends hours into a pipeline that cannot end
in an offer; a false NOT SPONSORABLE silently discards a viable role and the user never
learns it existed; an honest UNVERIFIABLE costs one manual re-check. False confidence
is the cardinal failure, in both directions.

The output is advisory only — the human decides whether to apply. No consequential action
is ever executed by the system (brief ground rules 04/05 satisfied by construction; CN-6
trivially).

---

## Why existing tools don't answer this

Job-board and scraper sponsorship filters answer "does the posting mention sponsorship",
not "can this requisition produce a Certificate of Sponsorship". In the author's own
search, a scrape of roughly 400 mid-level London software roles over a six-month window
returned 2 rows flagged as mentioning sponsorship. Employers who sponsor overwhelmingly
say nothing about it, so the filter's negatives are meaningless and its recall is near
zero — which is why C3 treats silence as indeterminate rather than as a refusal.

Register lookup tools answer presence only. They do not read the licence category, so a
Global Business Mobility-only licence — an intra-company transfer route, unreachable for
this user — reads as a positive. That is failure mode 2 in the ranked failure surface, and
it is the most expensive one, because it produces a confident false SPONSORABLE.

Nothing checks willingness at the requisition level. A licensed, A-rated employer
routinely publishes a role stating it cannot offer sponsorship. Holding a licence and
using it on this requisition are different facts, and only the posting settles the second
one.

Nothing applies the salary floor as a disqualifier. A role advertised below the
new-entrant rate cannot be sponsored regardless of licence or willingness, which silently
removes a whole band of otherwise-plausible early-career roles. The four checks are
individually available and never composed — and the composition is where the two-hop
failures live, which is exactly what the compound hard case in the evaluation
demonstrates.

---

## 2. The four checks as testable predicates

Stable vocabulary used everywhere (code, metrics, JSON, test names): `register`, `route`,
`willingness`, `salary`.

| # | Predicate | Signature | Definitive outcomes | Tests (T-4: named after the criterion) |
|---|---|---|---|---|
| C1 | `register` | `resolve_entity(employer_text, register_snapshot, aliases) -> Match \| NoMatch \| Ambiguous` | Match → pass; NoMatch after full alias resolution → fail; Ambiguous → indeterminate | `test_register_exact_legal_name_matches`, `test_register_trading_name_resolves_to_legal_entity`, `test_register_unlisted_employer_is_no_match`, `test_register_ambiguous_multi_entity_is_indeterminate` |
| C2 | `route` | `skilled_worker_route(entity_rows) -> pass \| fail` | Skilled Worker row present → pass; rows exist but GBM/other only → fail | `test_route_skilled_worker_present`, `test_route_gbm_only_fails`, `test_route_rating_blocks_cos_fails` *(ground truth per the case-schema amendment: a rating that blocks new CoS issuance is a definitive fail — archetype `licence_rating_blocks`. The solver-side sub-check stays Saturday-only-if-holds; until it lands, the case scores against the solver honestly)* |
| C3 | `willingness` | `sponsorship_stance(posting_text) -> offered \| refused \| silent \| ambiguous`, with verbatim quote spans | refused → fail; offered → pass; silent/ambiguous → indeterminate | `test_willingness_explicit_refusal_detected`, `test_willingness_negated_availability_detected`, `test_willingness_silence_is_not_refusal`, `test_willingness_right_to_work_boilerplate_is_ambiguous` |
| C4 | `salary` | `salary_clears_floor(parsed_salary, floor_config) -> pass \| fail \| indeterminate` | max of stated range < floor → fail; min ≥ floor → pass; range straddles floor, non-annual units, OTE, or absent → indeterminate | `test_salary_below_floor_fails`, `test_salary_range_straddling_floor_is_indeterminate`, `test_salary_above_floor_passes`, `test_salary_absent_is_indeterminate` |

**Verdict combinator** — a pure function, the only place a verdict is produced: any
definitive fail → NOT SPONSORABLE naming the failing check; all four definitive pass →
SPONSORABLE; otherwise UNVERIFIABLE listing exactly which checks are unresolved and why.
Tests: `test_verdict_all_pass_is_sponsorable`, `test_verdict_any_fail_is_not_sponsorable`,
`test_verdict_unresolved_check_is_unverifiable`,
`test_verdict_never_sponsorable_without_all_four_evidenced`.

Two approved policy points inside the predicates:

- **C3 silence.** Many genuinely sponsorable postings say nothing about sponsorship.
  Silence is indeterminate — it blocks SPONSORABLE but does not produce NOT SPONSORABLE.
  Honest consequence: clean SPONSORABLE verdicts are rare; the common good outcome is
  "register/route/salary pass, posting silent — ask before applying." That is the truthful
  shape of the domain.
- **C1 NoMatch.** "Not on the register" is only definitive after the full alias pass
  (normalisation + trading-name resolution). A NoMatch reached with unresolved ambiguity
  is indeterminate, not a fail.

The salary floor is **two thresholds, not one** (amendment at the case-schema review): a
Skilled Worker salary must clear BOTH the general threshold AND the SOC-specific going
rate — whichever is higher applies. `floor_config` carries both
(`general_threshold_gbp`, `going_rate_gbp` for SOC 2134 at the new-entrant basis), each
with its own effective date and source URL, and `salary_clears_floor` takes the maximum.
£38,300 is the operator-supplied going rate; the general-threshold amount is verified at
the label pass. Data, not code — never a literal. Thresholds change (April 2024,
July 2025 revisions); which rules snapshot was applied is part of the uncertainty
statement. `below_general_threshold` and `below_going_rate` are distinct fail reasons: a
solver checking one number passes a between-band salary wrongly, toward false
SPONSORABLE.

---

## 3. Failure surface of a naive one-prompt agent, ranked by harm to the user

Harm classes: **A** = wasted application (false SPONSORABLE), **B** = lost viable role
(false NOT SPONSORABLE), **C** = fabricated or unanchored evidence (erodes the only thing
the tool sells: trust), **D** = silent staleness.

| Rank | Failure mode | Class | Mechanism |
|---|---|---|---|
| 1 | World-knowledge substitution | A + C | Model "knows" a household-name employer sponsors ("Deliveroo is huge, of course they're licensed") and asserts register presence without a row. The register row is the fact; the model's prior is the enemy. |
| 2 | Route conflation | A | Entity found on register → verdict says sponsorable. The licence is GBM-only; the row literally exists, which is why one prompt gets it wrong — presence is a route-qualified fact. |
| 3 | Optimistic salary parse | A | "£30k–£42k", "up to £40k OTE", day rates: the model anchors on the top of the range or converts loosely, passes a role whose realistic offer sits below £38,300. |
| 4 | Missed negation in willingness | A | "We are unable to offer sponsorship at this time", "candidates requiring sponsorship will not be considered" — buried, negated, or hedged refusals read past by a single pass. |
| 5 | Ctrl-F entity matching | B | Trading name absent from register under its posted spelling → "not on register" → viable role discarded. The operating-company-vs-brand-name archetype. |
| 6 | Boilerplate misread | B | "Must have the right to work in the UK" treated as a refusal. It is ambiguous boilerplate, not a stance. |
| 7 | Wrong legal entity in a group | A or B | Agency postings, parent-vs-UK-subsidiary, multi-entity groups: the licence of the wrong entity gets checked. |
| 8 | Aggregator wrapper poisoning | A or B | Aggregator metadata (level tag, salary field) contradicts the posting body; the model trusts the structured-looking wrapper over the primary text. |
| 9 | Unanchored citations | C | Quotes that do not appear in the posting, register rows that do not exist in the snapshot. Enables 1–4 and is independently measurable. |
| 10 | Register staleness | D | Licences are revoked and suspended weekly; a verdict is only as fresh as the snapshot. Mitigation is honesty, not prediction: every verdict carries the snapshot date and an age warning. |

The baseline will demonstrably exhibit 1, 2, 3, 4, 6, 8 and 9, and a partial form of 5.
This table is the source of the baseline-to-advanced delta, of the case archetype matrix
in §7, and goes into the README and the video largely unchanged.

---

## 4. Baseline — one direct prompt with basic instructions

Per the brief's own definition of a fair simple baseline. `src/baseline/solve.py`,
buildable in under an hour, frozen after first green run (CN-3). Built **after** the case
set exists — the cases are the asset, the baseline is an hour.

- One Anthropic API call, pinned model, temperature 0, seeded harness (C-6).
- System prompt: the four checks described in plain language, the floor value, and the
  required output JSON schema (same schema as advanced — the harness compares like with
  like).
- Context: the requisition text, plus a naive register lookup — rows where
  `Organisation Name` contains the employer string case-insensitively (first 20 rows, or
  the literal line `NO ROWS MATCHED`). That is the honest automation of what a person does
  today: Ctrl-F the CSV.
- No retries, no tools, no verification, no second pass.

**Fairness statement (required by the brief):** baseline and advanced receive identical
inputs — requisition text, the same committed register snapshot, the same floor config.
The only difference is method.

**Predicted failure modes it will exhibit** (and which metric catches each):
world-knowledge substitution and unanchored citations → `grounding_rate`; route
conflation, optimistic salary, missed negation → `confident_wrong_rate` and per-check
`check_accuracy`; trading-name misses → `register` check accuracy; verdicts overall → low
`verdict_utility`. It should score visibly poorly on the adversarial archetypes while
passing the clean cases — that is exactly the delta the submission measures.

---

## 5. Advanced direction

| | Approach | Agent capability (brief's vocabulary) | Metric it moves | Risk | Time |
|---|---|---|---|---|---|
| **A — chosen** | **Extract → Resolve → Decide → Verify pipeline.** LLM extraction of typed claims from the posting (employer string, salary structure, stance quotes — Pydantic models, PY-2). Deterministic **tools** for entity resolution against the register: normalisation, legal-suffix and "t/a" stripping, fuzzy token-set match, alias table backed by cached Companies House name lookups (fixtures, offline). Pure-function rules engine computes each check and the verdict — code decides, not the model. Then an adversarial **verification** agent re-derives every check from the cited evidence alone, plus two mechanical gates: every quote must appear verbatim in the source, every cited register row must exist in the snapshot. Anything unsupported is downgraded to indeterminate → UNVERIFIABLE. | tools + verification | `confident_wrong_rate` ↓↓ (primary lever), `verdict_utility` ↑, `grounding_rate` → ~1.0 | Over-abstention: if resolution recall is poor, UNVERIFIABLE inflates on determinable cases. Watched via the abstention component of `verdict_utility`; mitigation is widening candidate generation, not loosening verification. | Sat, full day |
| B — not built | Four-specialist orchestration: one sub-agent per check plus a synthesiser. | orchestration | `check_accuracy`, marginally | Component count without purpose — the brief warns "purposeful choices matter more than the number of components". 4–5× cost, harder determinism. | — |

**Cut at planning (review 2026-08-28), recorded in DECISIONS.md:** the entity-resolution
memory layer. On a 30-case set it moves no metric visibly; a memory layer that exists to
be mentioned is exactly what the brief's purposefulness sentence penalises. Saturday
evening reallocates to the verification report (§5b) and the removed-experiment run.

**The removed experiment (kept, deliberate):** 3-sample self-consistency voting, run
Saturday evening through the same eval and rejected by its own numbers — expected outcome:
~3× `cost_per_case` without beating the verification layer on `confident_wrong_rate`. It
fills the changelog's and video's required removed-experiment slot honestly.

**Cost of being wrong about A:** if the true bottleneck turns out to be extraction quality
rather than resolution/verification, Saturday morning is spent polishing the wrong stage.
This is detectable by midday from the per-check `check_accuracy` breakdown (that is what
the metric is for), and the pivot is cheap because the stages are decoupled — reinvest in
extraction prompts (skills) without touching the rest.

---

## 5b. The verification report — the user-facing deliverable

End-to-End Quality is 20 of 100 and is judged on whether the intended user would consider
the output high quality rather than an obvious AI-generated draft. The deliverable to the
user is not a JSON dump; it is a **human-readable verification report for a single
requisition**, first-class, unit-tested, shown in the video.

Contents, in order:

1. The verdict, and immediately under it the single sentence that determines it.
2. Each of the four checks with its status, the verbatim quote that evidences it with a
   character offset into the source, and — where the register is the evidence — the
   register row (organisation name, town, type and rating, route) reproduced as it appears
   in the snapshot.
3. The snapshot date and an explicit age warning: licences are revoked and suspended
   continuously, and a verdict is only as fresh as its snapshot.
4. An uncertainty statement naming exactly what could not be established and what the user
   would have to do to establish it.
5. A closing line making clear this is advisory and the applicant decides.

Written as something a person would read before spending an application, in plain
English — no hedging boilerplate, no restating the input back at the reader.

**Design decision:** the report is produced by a deterministic pure renderer,
`render_report(verdict_obj, register_meta) -> str` — no LLM in the render path. The
sentences are written once, by a human, well; an LLM-per-report would reintroduce
nondeterminism and the exact "AI draft" smell the rubric penalises. Consistent with the
binding principle: code decides, the model extracts.

Tests (family): `test_report_leads_with_verdict_and_determining_sentence`,
`test_report_quote_offsets_are_valid_spans_of_source`,
`test_report_reproduces_register_row_verbatim`,
`test_report_states_snapshot_date_and_age_warning`,
`test_report_uncertainty_names_each_unresolved_check`,
`test_report_closes_with_advisory_line`.

Per BP-4: this component moves no eval metric and that is stated openly — it targets the
20-point judged criterion directly. The changelog entry says exactly that.

---

## 6. Metrics

Problem-specific additions to `eval/metrics.py` (all deterministic given labels; model
non-determinism handled by `--repeats 5` variance, already in the harness):

| Metric | Definition | Direction | Computed how |
|---|---|---|---|
| `verdict_utility` **(primary)** | Per case: **+1.0** correct verdict (including UNVERIFIABLE where ground truth is genuinely unverifiable); **+0.25** UNVERIFIABLE where truth was determinable (safe abstention, partial credit); **−1.0** confident wrong (S or NS that is wrong). Mean over cases, range [−1, 1]. | ↑ | Pure comparison against labels. Encodes the required asymmetry: a confident wrong answer scores 1.25 points below an honest abstention. |
| `confident_wrong_rate` | Wrong verdicts ÷ cases where the system issued a definitive S/NS. | ↓ | Label comparison. Captures baseline failure modes 1–4 directly. |
| `check_accuracy` | Macro-average agreement of the four per-check statuses with per-check labels. | ↑ | Label comparison. The diagnostic that attributes each iteration's delta to a stage — feeds the changelog. |
| `grounding_rate` | Mechanically verified citations ÷ citations issued: quote is a verbatim substring of the source; cited register row exists in the snapshot. | ↑ | String containment + CSV lookup. Catches fabrication (failure 9) with zero LLM cost. |
| `cost_per_case` | USD from token usage × pinned price table (documented in DECISIONS.md). | ↓ | Read from API usage fields at run time. |

Generic metrics kept: `error_rate`, `p50_seconds`, `p95_seconds`. `exact_match` is
narrowed to subset-match on the keys present in `expected` (verdict + per-check
statuses) — a metric-definition change, recorded in DECISIONS.md **before** the baseline
freeze so no results are ever incomparable.

**Brief's summary-table mapping:** Primary outcome = `verdict_utility`. Human time per
task = **time-to-a-trustworthy-answer**, measured Sunday (checkpoint 2026-08-29): three
requisitions, both variants, timed to the point the user could act on the output —
including the time to verify or refute a wrong or unsupported answer against the
register. Raw latency is not the claim: the baseline answers in about a minute and is
confidently wrong on a large fraction of definitive verdicts, so its verification cost
is part of its time. The advanced system's claim is that its output can be acted on
without re-derivation because every check carries a mechanically grounded citation.
Committed as an evidence file. Cost per task = `cost_per_case`. Every number in README
traces to an `eval/results/` file (CN-1).

**Metric integrity — three reference lines.** With the labelled mix (14/6/10), always
answering UNVERIFIABLE scores `verdict_utility` 0.5 for free. The harness therefore runs
a zero-cost `always_abstain` variant by default alongside baseline and advanced; every
results table carries all three, and the claim is "advanced beats both the baseline and
the trivial-abstention floor". Recorded in DECISIONS.md before the baseline freeze.

---

## 7. Evaluation design

**The cases are synthetic — and they are the first execution task, before the baseline.**
Real labelled URLs exist but early-career postings die within 48 hours; recovering dead
posting text is not a plan. Instead ~30 synthetic requisition fixtures are authored,
modelled on real archetypes personally encountered and documented by the author: fictional
company names, fictional postings, real structural patterns. Faster, cleaner on
redistribution (CN-7 explicitly prefers generated fixtures), full control over per-check
labels, and coverage built from the matrix rather than from whatever happened to survive.

- **Authoring flow with two human gates (TR-4):** (1) the agent produces the case JSON
  schema plus one fully filled example — the compound hard case, so the hardest case
  stress-tests the schema → **HUMAN review**. (2) The agent generates the full set per the
  archetype matrix → **HUMAN label-correction pass**. The labels are the ground truth and
  must be independently derived (T-7): each case is constructed *to be* its archetype (the
  register fixture row, the salary figure, the stance wording are chosen by design), and
  the human pass verifies every label rather than trusting the agent's fixture prose.
- **Archetype matrix (each encountered in practice; ≥2 cases per archetype where sensible,
  ~30 total):** licensed employer whose posting states verbatim it cannot sponsor ·
  trading name absent from register while the legal entity is present · GBM-only licence,
  no Skilled Worker · salary below the new-entrant floor at an otherwise perfect employer ·
  aggregator wrapper whose level tag or salary field contradicts the body · employer
  genuinely absent under every alias · clean positive (licensed, route, salary,
  sponsorship offered) · clean silent — ground truth UNVERIFIABLE · salary absent — ground
  truth UNVERIFIABLE · ambiguous multi-entity group — ground truth UNVERIFIABLE ·
  right-to-work boilerplate that is NOT a refusal · salary clearing the general
  threshold but below the SOC going rate (the strongest salary case: a one-number solver
  passes it wrongly) · licence rating that blocks new CoS issuance despite a Skilled
  Worker route row · compound hard case (below).
  Genuine-UNVERIFIABLE archetypes ensure abstention has true positives, so
  `verdict_utility` can't be gamed by never abstaining or always abstaining.
- **Register snapshot stays REAL** — public, Open Government Licence, and what makes the
  task non-toy. Synthetic employers are appended as clearly flagged fixture rows:
  realistic fictional names, with the exact list and row count documented in
  `docs/DATA.md` (plus a machine-readable manifest) so a judge can tell real rows from
  fixture rows at a glance — no in-band marker the system could exploit. Companies House
  alias lookups cached as fixtures. **The eval never touches the network**; live URL fetch
  exists only as a demo-mode flag.
- **Schema sketch** (locked by the Friday example): `{id, meta: {archetype, authored,
  split}, payload: {requisition_text}, expected: {verdict, checks: {register, route,
  willingness, salary}, evidence_anchors}}`. Aggregator cases embed the wrapper text in
  `requisition_text` exactly as a person would paste the whole page.
- **Split.** Develop against 20; hold out 10 untouched until the final Sunday eval.
  Changelog entries cite dev-set numbers; the README headline table reports the full set
  with the held-out breakdown. **Holdout discipline, in force from the case-set commit:**
  while building the solution, no `split: holdout` file is opened, read, quoted, or
  reasoned about; the eval runs `--split dev` (the harness default) until the final
  Sunday `--split all` run. Recalled holdout content is recorded in the trajectory, not
  silently used. Mechanical guard: the `--split` flag in `eval/run_eval.py`.
- **The hard case.** The compound: aggregator-hosted posting, brand name only, whose legal
  entity holds a **GBM-only** licence. A naive agent fails twice in sequence — resolves
  the name by vibes, then reads register presence as sponsorability — and both failures
  push toward false SPONSORABLE, the worst outcome. **What it reveals:** register presence
  is a route-qualified fact, and entity resolution must complete before the route is read.
  It justifies the pipeline architecture and fills the brief's "one challenging case"
  requirement.

10+ cases is exceeded from day one, with per-check labels by construction — the
evaluation asset most submissions won't have.

---

## 8. Schedule

Kickoff was 16:00 London, Fri 28 Aug.

| When | What | Exit condition |
|---|---|---|
| **Fri eve — first task** | Case schema + filled example (compound hard case) → **HUMAN review** → generate full ~30 synthetic set → **HUMAN label-correction** → register snapshot fetched once, committed compressed, fixture rows appended, DATA.md provenance → metrics into `metrics.py` + DECISIONS entries. | Case set authored, labels human-verified. |
| **Fri night** | Baseline built (≤1 h), first green run, `--repeats 5` noise floor, **frozen**; CHANGELOG `[0]`; trajectory. | Baseline green and frozen tonight. |
| **Sat AM** | Extraction + entity-resolution tools, unit tests first (C-1). | Resolution passes the trading-name tests. |
| **Sat midday** | Wire pipeline, first advanced-vs-baseline eval → CHANGELOG `[1]`. Check `check_accuracy` breakdown; pivot here if extraction, not resolution, is the bottleneck. | Measured delta exists. |
| **Sat PM** | Verifier + rules engine → `[2]`. | `grounding_rate` ≈ 1.0, `confident_wrong_rate` down. |
| **Sat eve** | Verification report renderer + tests → `[3]` (moves no eval metric — stated per BP-4); self-consistency experiment run through the same eval → `[x]` rejected by its numbers. | Report renders on every dev case; changelog has a rejected experiment with numbers. |
| **Sun AM** | Prompt 03 hardening: QREPRO from a clean container, hostile inputs (T-9), staleness warnings. | REPRODUCTION.md executes literally, clean clone. |
| **Sun midday** | Final eval: full 30 + held-out breakdown + variance. | The README headline numbers exist in `eval/results/`. |
| **Sun PM** | README, CHANGELOG, REPRODUCTION, DATA, DECISIONS complete; time-to-a-trustworthy-answer measurement (three requisitions, both variants, verification time included — checkpoint 2026-08-29); trajectories audit. | Every claim traces to a file (CN-1). |
| **Sun eve** | Video (≤5 min: problem → baseline failing live on the hard case → advanced producing the verification report on the same case → metric table → the removed experiment) → **submit**. | Submitted Sunday night. |
| **Mon ≤18:00 UTC** | Reserve only: re-verify reproduction from a fresh clone; re-record video if needed. Nothing new lands Monday. | — |

**Cut order if it slips:** 1) the B-rating sub-check (folded into the uncertainty
statement); 2) the Companies House alias layer — fall back to normalisation + fuzzy
matching, accept higher UNVERIFIABLE, and say so honestly; 3) the held-out split (report
full-set numbers and disclose); 4) the removed-experiment run — last resort, since it
costs the changelog its rejected-experiment entry. **Never cut:** the frozen baseline, the
evidence chain, REPRODUCTION.md, trajectories, the video, the verification report — each
is a MUST, a deliverable, or 20 judged points.

**Submission-form constraints (discovered at the form, 2026-08-28):** source code is
submitted as a zip with a **hard 50MB limit**; the video is submitted as a **URL only**
(no file upload). The register snapshot is the only artifact that threatens the limit: it
is committed gzipped, never raw, and `git archive HEAD | wc -c` is checked after the
snapshot commit. If the archive does not fit comfortably, the snapshot is filtered to the
rows the cases and resolution tests need, with the filter script committed and the
before/after row counts documented in `docs/DATA.md` — a filtered snapshot is honest if
the filter is committed and described; a snapshot that silently omits rows is not.

---

## Approval record — confirmed decisions (2026-08-28)

1. **Cases:** synthetic fixtures authored from the documented archetype matrix; authoring
   is the first execution task; labels are human-verified ground truth (T-7). Real
   register snapshot with flagged fixture rows per §7.
2. **Scope:** software-engineering requisitions; SOC 2134; new-entrant rate. Floor
   **£38,300** as versioned config carrying rate, SOC code, effective date, source URL —
   never a literal in code.
3. **Stack:** Python only; Node/TS scaffold stays unused. Pinned additions to
   `docker/requirements.txt`, each justified per C-9: `anthropic`, `pydantic`, `rapidfuzz`.
4. **Input contract:** pasted requisition text. URL fetching is demo-mode only, behind a
   flag; the eval never goes to the network.
5. **Model:** identical pinned model and temperature 0 for baseline and advanced; model ID
   and price table recorded in DECISIONS.md at implementation time.
6. **B-rating sub-check:** only if Saturday holds; otherwise it lives in the uncertainty
   statement. Do not let it grow.
7. **Memory approach:** cut at planning; recorded in DECISIONS.md. Removed-experiment slot
   filled by self-consistency voting instead.
8. **Verdict combinator:** stays a pure function. Code decides, the model extracts; a
   model is never the last thing between evidence and a verdict.

## Verification

- Every predicate in §2 and every report property in §5b lands as a named failing test
  first (C-1); suite plus gates G-1–G-4 green before any commit claiming a result.
- `python eval/run_eval.py --variant baseline --variant advanced --seed 42` is the single
  source of every number; `--repeats 5` establishes the noise floor before any delta is
  claimed.
- QREPRO from a clean container on Sunday is the qualification gate; a reproduction break
  is a blocker regardless of metric gains (CN-2).

## Next step

Run `prompts/01-baseline.md` with the amended ordering: **first** the case schema + filled
example for human review, then the full synthetic set for the label-correction pass, then
the register snapshot and metrics, then the baseline build and freeze. This document seeds
README's user/bottleneck sections, DECISIONS.md's planning entries, and the changelog's
hypothesis language.

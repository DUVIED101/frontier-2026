# Decisions

Why, not what. One entry per real decision: a tradeoff taken, an alternative rejected, a
constraint discovered. The README's "main failure mode" and the video's "one experiment
you removed" are both written out of this file, so keep it honest and keep it current.

## Template

```markdown
### <YYYY-MM-DD> — <decision, stated as the choice made>
**Context.** What forced a choice.
**Options.** A / B / C, with the cost of each.
**Chosen.** Which, and the deciding factor.
**Rejected.** What was given up, and under what conditions the other option would win.
**Evidence.** eval/results/<file>.json, if the decision was measured rather than reasoned.
```

---

### 2026-08-28 — Baseline is frozen after its first green run
**Context.** The submission is scored on measured improvement between two solutions.
**Options.** (A) Keep the baseline current with shared refactors. (B) Freeze it entirely.
**Chosen.** B. A drifting reference makes every reported delta uninterpretable, and shared
code between the two variants means an "improvement" can come from a change to the baseline.
**Rejected.** Some duplication between `src/baseline/` and `src/advanced/` is accepted as the
price of a clean comparison.
**Evidence.** Reasoned, not measured.

### 2026-08-28 — Evaluation harness written before the problem is known
**Context.** Scoring gate is reproducibility; a submission that cannot be verified is not
scored at all.
**Options.** (A) Build the harness after the solution, when metrics are obvious.
(B) Build it first, with generic metrics, and add problem-specific ones after kickoff.
**Chosen.** B. Metrics written after the solution tend to be the ones the solution happens to
win on, and under time pressure the harness is what gets cut.
**Rejected.** Some harness code may go unused if the problem prescribes its own test runner.
**Evidence.** Reasoned, not measured.

### 2026-08-28 — Synthetic case fixtures instead of recovered live postings
**Context.** The labelled real cases exist as verdicts and URLs, not saved posting texts,
and early-career postings close within 48 hours — a large fraction of the links are dead.
Recovering text from dead links on the first evening is not a plan.
**Options.** (A) Recover and redact real postings. (B) Author ~30 synthetic fixtures
modelled on real archetypes the author has personally encountered and documented.
**Chosen.** B. Faster, cleaner on redistribution (CN-7 explicitly prefers generated
fixtures), full control over per-check labels, and coverage built from the archetype
matrix rather than from whichever postings happened to survive. The sponsor register
snapshot stays real (Open Government Licence); synthetic employers are appended as fixture
rows flagged in `docs/DATA.md`. Labels are human-verified ground truth (T-7), never
inferred from the fixture prose by the agent that wrote it.
**Rejected.** The realism of found text — accepted because the structural patterns, not the
prose, are what the checks exercise.
**Evidence.** Reasoned, not measured.

### 2026-08-28 — Entity-resolution memory layer cut at planning
**Context.** Saturday has room for one secondary component beside the core pipeline; the
brief warns that purposeful choices matter more than the number of components.
**Options.** (A) Persist an employer→legal-entity map across runs, keyed by register
snapshot date. (B) Cut it now.
**Chosen.** B. On a 30-case evaluation it moves no metric visibly; a memory layer that
exists to be mentioned is exactly what the brief's purposefulness criterion penalises.
The evening reallocates to the verification report and the removed-experiment run.
**Rejected.** Faster repeat lookups and cross-run consistency — worth revisiting only in
real daily use, where the same employers recur across dozens of checks.
**Evidence.** Reasoned, not measured.

### 2026-08-28 — Self-consistency voting kept as the deliberate removed experiment
**Context.** The changelog and the video each require one experiment that was tried and
removed, with the lesson it taught.
**Options.** (A) A stripped four-specialist orchestration variant. (B) 3-sample
self-consistency voting over the single-call solver.
**Chosen.** B. Cheaper to build and to run, and the expected result is instructive:
roughly 3× `cost_per_case` without beating deterministic verification on
`confident_wrong_rate`, because sampling the same prompt three times resamples the same
blind spots. It must be actually run through the same eval and rejected by its own
numbers, not dismissed on argument.
**Rejected.** The orchestration variant — more expensive to build for the same lesson.
**Evidence.** To be measured Saturday evening; the entry is not written until the
`eval/results/` file exists.

### 2026-08-28 — `exact_match` narrowed to subset-match before the baseline freeze
**Context.** Solver output carries evidence and uncertainty fields; whole-dict equality
against `expected` would read 0 for every variant and make the generic correctness metric
meaningless.
**Options.** (A) Keep whole-dict equality. (B) Compare only the keys present in
`expected` (verdict + per-check statuses).
**Chosen.** B, decided now — before any results exist — so no recorded run is ever
incomparable under the metric-change rule in `eval/metrics.py`.
**Rejected.** Strict whole-structure equality, which T-5 favours in tests; the eval metric
instead measures the decision surface, and structure is asserted in unit tests.
**Evidence.** Reasoned, not measured.

### 2026-08-28 — Verification report rendered deterministically, no LLM in the render path
**Context.** End-to-End Quality (20 of 100) is judged on whether the intended user would
consider the output high quality rather than an obvious AI-generated draft. The
user-facing deliverable is a plain-English verification report.
**Options.** (A) Have a model write each report from the verdict object. (B) A pure
renderer `render_report(verdict_obj, register_meta) -> str` with human-written sentence
templates.
**Chosen.** B. A model per report reintroduces nondeterminism and the exact "AI draft"
register the rubric penalises; a pure renderer is unit-testable, free, and consistent with
the binding principle that code decides and the model extracts.
**Rejected.** Per-report prose variety — the report is a fixed instrument, and sameness
across requisitions is a feature for comparison, not a defect.
**Evidence.** Reasoned, not measured. Moves no eval metric (BP-4); targets the judged
End-to-End Quality criterion.

### 2026-08-28 — always_abstain added as a third reference variant (metric integrity)
**Context.** The labelled verdict mix is 14 NOT_SPONSORABLE / 6 SPONSORABLE /
10 UNVERIFIABLE, so the strategy "always answer UNVERIFIABLE" scores verdict_utility
0.5 — half of maximum — with no model call. A property of the metric, not a labelling
error, and one a judge will find.
**Options.** (A) Rebalance the case distribution or re-weight the scoring to punish
abstention. (B) Expose the floor: a zero-cost `always_abstain` variant in the harness,
run by default alongside baseline and advanced.
**Chosen.** B. The distribution reflects the real archetype mix and the scoring asymmetry
is the point of the metric; tuning either to defeat a degenerate strategy would bend the
eval toward the metric. Making the floor visible turns the claim into "advanced beats
both the baseline and the trivial-abstention floor", which survives scrutiny. This entry
also sanctions the runner edits (default variant list of three; `summarize()` shows no
pairwise delta at three columns — deltas for README come from the results JSON).
**Rejected.** Rebalancing. It would also have destroyed comparability with the authored
archetype coverage.
**Evidence.** Arithmetic from the labels: (10 × 1.0 + 20 × 0.25) / 30 = 0.5. Recorded
before the baseline freeze.

### 2026-08-28 — Holdout enforced mechanically via --split, default dev
**Context.** All 30 cases including the 10 holdout were necessarily read at authoring.
The discipline that matters is that Saturday's prompts and resolution rules are not tuned
against holdout content, and a promise is not a mechanism.
**Options.** (A) Rely on conduct alone. (B) Add `--split dev|holdout|all` to the harness
with `dev` as the default, so the development loop cannot silently include holdout cases;
the final Sunday run passes `--split all` explicitly.
**Chosen.** B, plus the conduct rule in force from the case-set commit: do not open,
read, quote, or reason about `split: holdout` files while building the solution; if
holdout content is recalled during design, record it in the trajectory rather than
silently proceeding. This entry sanctions the runner edits below the do-not-edit line
(split argument, split filtering in `load_cases`, split recorded in the results file).
**Rejected.** Default `all` — it would make the canonical dev command include holdout by
default, inverting the failure mode the flag exists to prevent.
**Evidence.** Reasoned, not measured. Recorded before the baseline freeze.

### 2026-08-28 — Model pinned to claude-sonnet-4-6, temperature 0 via extra_body
**Context.** The approval record requires one identical pinned model for baseline and
advanced, and a pinned temperature (C-6). The current API reference (cached 2026-06-04,
checked tonight): sampling parameters are removed on Opus 4.7/4.8 and Fable 5 — sending
`temperature` returns a 400 — but remain accepted on the 4.6 family.
**Options.** (A) claude-opus-4-8 without a temperature pin. (B) claude-sonnet-4-6 with
temperature 0. (C) claude-haiku-4-5 with temperature 0.
**Chosen.** B. Only the 4.6 family satisfies the temperature pin; Sonnet 4.6 is the
strongest of them; $3/$15 per MTok keeps a ~150-call evening (noise floor + reference
table) around $2; both variants use the identical model per the fairness statement.
Dead end worth recording: anthropic SDK 1.2.0 has already dropped sampling parameters
from the typed `messages.create` signature (caught by mypy --strict), so the pin passes
through `extra_body` — the API accepts it for this model, and a wrong model/parameter
combination fails loudly with a 400 rather than silently sampling. Prices recorded in
`eval/metrics.py::MODEL_PRICES_USD_PER_MTOK` for `cost_per_case_usd`.
**Rejected.** A — highest capability, but no temperature pin and several times the price
for an eval loop whose baseline exists to be beaten. C — cheapest, but weakens the
baseline for no reason the metrics need.
**Evidence.** Parameter support and prices from the API reference; the SDK signature
verified against anthropic==1.2.0 under mypy --strict.

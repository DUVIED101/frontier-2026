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

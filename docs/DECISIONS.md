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
**Evidence.** Measured 2026-08-29: `eval/results/20260829-092222.json` — rejected,
worse than predicted (verdict_utility 0.225 vs same-run baseline 0.425 at 3.07× the
cost; two NEW wrong verdicts from temperature diversity; check_accuracy unchanged).
CHANGELOG entry [5].

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

### 2026-08-29 — Baseline lookup guard is specificity, not a threshold; prompt rolled back once
**Context.** The first noise-floor run exposed two problems before the freeze. (1) A
defect: the lookup's first-candidate-wins rule let job-title segments that survive the
stopword list ("Integrations", "Payments", "Reporting") substring-match unrelated
register rows and shadow the employer's name — on 5 of 20 dev cases the employer's row
never reached the model, which then truthfully reported the employer absent. (2) The
system prompt narrated the author's expertise: both thresholds with "the higher of the
two applies", the guaranteed-basic-pay exclusion list, the full reason vocabulary, the
verdict-combination rules. Case-11 was answered correctly *because the prompt contained
the answer key*.
**Options.** For (1): a hit-count threshold ("skip candidates matching > N rows") — but
"Integrations" matches only 6 register orgs, so any threshold separating it from a real
name's 1–3 hits would be tuned to cases, which the fix's own scope condition forbids.
Or specificity ordering: among candidates with 1..MAX_REGISTER_ROWS hits, fewest hits
wins; more hits than the excerpt carries means "generic word, not a name". For (2): keep
the strong prompt and accept a baseline that answers its own exam, or roll back once to
plain-language questions with the floor figures attached as data, then accept the
re-gate outcome without iterating.
**Chosen.** Specificity ordering (parameter-free, encodes only "this is not a name"),
pinned by a test that fails on the old behaviour; and the one-time rollback. Binding
conditions recorded at approval: the rollback happens once and the re-gate outcome is
final — tuning the baseline downward until designed failures fire would bend the eval;
and the same discipline binds the advanced variant: interpretation coaching removed
from the baseline prompt must not reappear hardcoded in the advanced extraction prompt.
Threshold logic lives in the rules engine, as code, reading floor_config. Code decides,
the model extracts.
**Rejected.** Stoplist additions (whack-a-mole; per-case knowledge in disguise) and any
second prompt pass.
**Evidence.** eval/results/20260828-224144.json (the defect-depressed run — recorded as
superseded, NOT the baseline; the rubric asks for gains over a fair baseline) and the
post-fix rerun committed alongside the freeze.

### 2026-08-29 — Case-01 cannot discriminate at verdict level; kept as a check-level case
**Context.** Case-01's designed failure is world-knowledge substitution: a naive agent
resolves a brand by prior ("of course they sponsor") and reads register presence as
sponsorability, pushing toward false SPONSORABLE. Under a live model the trap never
fired — and inspection shows it cannot: every fixture employer is fictional, so no
model holds a prior about any of them. For a fictional brand the lookup finds nothing
and NOT_SPONSORABLE-via-no_match collapses onto the correct verdict for any baseline.
**Options.** (A) Introduce real-brand cases to elicit the failure — reopens the
redistribution and staleness problems the synthetic decision closed. (B) Relabel or
drop the case. (C) Keep it as a check-level discriminator: at verdict level it cannot
separate variants, but the evidence chain (register pass/alias_lookup with the entity's
row, versus fail/no_match) separates them fully via check_accuracy and grounding_rate.
**Chosen.** C, with the limitation stated in README's failure-mode section: the
highest-harm failure mode in the design is one this evaluation structurally cannot
elicit. The honest sentence is worth more than a case that pretends to measure it.
**Rejected.** A — it would trade a stated limitation for a data-provenance problem two
days before submission.
**Evidence.** eval/results/20260828-224144.json (case-01: correct verdict, wrong
evidence chain, exactly as the structural argument predicts).

### 2026-08-29 — decisive_accuracy and decisive_rate added, with a pre-registered target
**Context.** always_abstain scores verdict_utility 0.5125 on the dev mix. The advanced
design's verification layer works by downgrading unsupported claims to indeterminate —
it moves the system toward abstention. There is a real outcome where advanced lands at
0.55–0.60: above both reference lines, and barely better than answering UNVERIFIABLE to
everything. verdict_utility cannot tell that outcome from a good one.
**Options.** (A) Rebalance utility weights to punish abstention — bends the metric that
encodes the domain's real asymmetry. (B) Add a coverage/precision pair:
decisive_accuracy = correct definitive verdicts ÷ definitive verdicts issued;
decisive_rate = definitive verdicts issued on determinable cases ÷ determinable cases.
always_abstain scores 0 on decisive_rate by construction.
**Chosen.** B, before any advanced code exists, with the target recorded now so it
cannot be adjusted afterwards: **advanced must beat the baseline on verdict_utility AND
beat always_abstain on decisive_rate while holding decisive_accuracy high. Passing
verdict_utility by abstaining more is not the claimed result.**
**Rejected.** A. The asymmetry is the point of the primary metric; coverage is a
separate axis and gets its own metrics.
**Evidence.** Arithmetic from the labels; metrics added with hand-computed unit tests
before the freeze, so every recorded run from the freeze onward carries them.

### 2026-08-29 — Human time is measured as time-to-a-trustworthy-answer
**Context.** The draft framing claimed 10–20 minutes of manual cross-referencing per
requisition. That describes someone working with the raw CSV; the author's actual
process is one direct prompt against a chat with the register loaded — about a minute,
and exactly what src/baseline/solve.py implements. "15 minutes versus one minute" is
therefore not an honest claim, and raw latency is not the bottleneck at all.
**Options.** (A) Report solver latency as the human-time win. (B) Define the metric as
time-to-a-trustworthy-answer: time until the user can act on the output, including the
time to verify or refute a wrong or unsupported answer against the register.
**Chosen.** B. The baseline produces text in a minute and is confidently wrong on
roughly half its definitive verdicts, so acting on it requires re-deriving it — the
verification cost is part of its time. The advanced system's claim is that its output
can be acted on without re-derivation because every check carries a mechanically
grounded citation. Sunday protocol, fixed now: three requisitions, both variants, timed
to the act-on-it point, wrong/unsupported answers verified by hand, committed as an
evidence file. A second consequence is recorded in README: the baseline is a faithful
reproduction of the manual process in use today — the brief's "manual process people
use today" baseline, qualifying literally.
**Rejected.** A, and the 10–20-minute figure everywhere — it survives nowhere in the
repo outside the trajectory record of this correction.
**Evidence.** To be produced Sunday as the timing evidence file; until then no
human-time number appears in any judged document.

### 2026-08-29 — Re-gate ruling applied: case-13 re-designated; the accepted baseline
**Context.** The acceptance criterion recorded before the rerun: a gate case the fixed
baseline answers correctly with correct evidence is a finding about current models, not
a defect, and is re-designated a check-level discriminator. On the rerun
(eval/results/20260829-002003.json) case-13 was answered NOT_SPONSORABLE with the
correct evidence chain throughout: the model chose the posting body's £29,000 over the
aggregator wrapper's £45,000 unprompted, twice now, under two different prompts.
**Options.** Per the pre-registered criterion — no options were open. This entry
records the application, not a choice.
**Chosen.** Wrapper-metadata poisoning (docs/PLAN.md §3 failure 8) is not a live
failure mode for the pinned model at baseline prompt strength. Case-13 converts from a
verdict-level trap to a regression guard: any variant that gets it wrong has regressed
below today's manual process. Cases 07 (route conflation via the Type & Rating column,
false SPONSORABLE), 11 (failing salary check waved through to SPONSORABLE without
combination rules), and 26 (right-to-work boilerplate read as refusal) fired as
designed and stay verdict-level discriminators; case-01 stays check-level per its own
entry. The rerun is the accepted baseline per Condition A: no second pass.
**Rejected.** Nothing — the bar was set before the number, which is the point of
setting it first.
**Evidence.** eval/results/20260829-002003.json; acceptance criterion in the
2026-08-28-1833 trajectory, recorded before the rerun launched.

### 2026-08-29 — Tagged runs refuse a dirty tree; no citation from a git_dirty file
**Context.** Third dirty-tree incident of the weekend: eval/results/20260829-210352.json
— the flag-less three-variant run pasted into REPRODUCTION §6 — records
git_dirty=true, so it does not reproduce from fd25c6e, which is the point of the
field. An audit of all twenty committed results files found six recording git_dirty,
including 20260829-205909 (the §5 paste; same SHA as the clean §4 run 205818, so the
tree went dirty between the two runs — the §4 output was being pasted into
REPRODUCTION.md while §5 ran). Every one of the six was tagged. The existing
behaviour warned after the run — after the money was spent.
**Options.** (A) Keep the warning and remember the lesson — already failed twice.
(B) Refuse tagged runs from a dirty tree before any model call. Within B: refuse on
any porcelain output, or exempt untracked files under eval/results/.
**Chosen.** B with the exemption. `--tag` marks a run as a source of record; the
harness now refuses to start when the tree carries anything beyond untracked files
under eval/results/. The exemption is forced by CN-2: a fresh-clone verifier
following REPRODUCTION in order accumulates untracked results files from §§4–6
before reaching the tagged final command, and those files are the harness's own
outputs, never inputs — refusing on them would break the reproduction guide the
guard exists to protect. The recorded git_dirty field keeps its raw meaning (any
porcelain output), so a verifier's tagged run may still truthfully record dirty
while being allowed to start. Standing rule to submission, recorded in prompts/02:
no number reaches README, CHANGELOG or the video from a results file recording
git_dirty — the guard prevents new such files; the rule covers the six that predate
it.
**Rejected.** Refusing on any dirt (breaks CN-2 as above). Refusing untagged runs —
the dev loop legitimately runs mid-edit and the warning suffices there.
**Evidence.** tests/test_run_eval.py (six tests, red before the guard existed); the
audit list in the 2026-08-29-0757 trajectory, checkpoint 9; the refusal exercised
live against this change's own dirty tree before commit — exit 2, no results file,
no model call.

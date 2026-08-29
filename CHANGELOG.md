# Improvement Changelog

One entry per meaningful iteration, newest first. Each entry is connected to the evidence
that guided the next decision, per the submission requirements.

**Rules for every entry:**
- Numbers must match the cited `eval/results/` file exactly. If there is no file, there is no claim.
- Record what the evidence made you do next. That link is the point of the document.
- Discarded experiments get entries too. The solution video explicitly asks for one experiment
  that was removed — this is where it comes from.

---

## Entry template — copy this, do not improvise

```markdown
### [N] <short imperative title>
`<commit sha>` · <YYYY-MM-DD HH:MM> · trajectory: `trajectories/<file>.md`

**Hypothesis.** What was expected to improve, and why that was a reasonable guess.

**Change.** What was actually built. Files touched.

**Measurement.** Evidence: `eval/results/<file>.json`

| Metric | Before | After | Delta |
|---|---|---|---|
| | | | |

**Verdict.** KEPT / REVERTED / PARTIAL — and the reason, in the numbers.
Is the delta larger than run-to-run variance? State the variance.

**What this told me to do next.** The decision the evidence forced.
```

---

## Log

### [4] Stance extractor learns that right-to-work wording settles nothing
`f9f9c31` · 2026-08-29 08:53 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** case-26 flips NOT_SPONSORABLE → UNVERIFIABLE (correct abstention):
verdict_utility +0.10 (a −1.0 becomes +1.0 on one of twenty cases), with case-27 (RTW
wording PLUS an explicit refusal) as the regression sentinel that must stay
NOT_SPONSORABLE.

**Change.** One stance-definition refinement in `extract.py`'s prompt, stated as the
general principle rather than the case: sponsorship itself confers the right to work,
so an RTW requirement alone is "ambiguous", never "refused"; "refused" now requires
an explicit statement that sponsorship is unavailable or sponsorship-needing
candidates excluded. No threshold, route or verdict logic — extraction semantics only
(Condition C respected).

**Measurement.** Evidence: `eval/results/20260829-085330.json`

| Metric | baseline (same run) | advanced | Delta |
|---|---|---|---|
| verdict_utility | 0.225 | **0.9** | +0.675 |
| confident_wrong_rate | 0.4667 | **0.0769** | −0.390 |
| decisive_accuracy | 0.5333 | 0.9231 | +0.390 |
| decisive_rate | 0.8462 | 1.0 | +0.154 |
| check_accuracy | 0.8 | 0.9875 | +0.188 |
| grounding_rate | 0.9691 | 1.0 | +0.031 |
| cost_per_case_usd | 0.01111 | 0.00312 | −72% |

case-26: UNVERIFIABLE with `willingness: indeterminate/boilerplate_ambiguous` — the
exact labelled reason. case-27 sentinel: NOT_SPONSORABLE with `fail/refused` — no
regression. Advanced verdict delta vs its own previous runs: +0.10, exactly the
hypothesis; four prior runs were identical at 0.8, so this is signal, not noise.

**Verdict.** KEPT. 19/20; the single remaining wrong verdict is case-28, the
deliberately cut B-rating sub-check (scope ruling 2026-08-29), whose price is known,
bounded, and stated in that output's own uncertainty statement.

**What this told me to do next.** The dev-split failure surface inside scope is
clear. Next per plan: the verification report renderer (Sunday morning, first), the
removed-experiment run (self-consistency), and the final `--split all` evaluation.

### [3] Verifier gates model-sourced quotes ahead of the combinator
`7c85ed0` · 2026-08-29 08:47 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** Zero dev delta — extraction quotes have been verbatim in every
recorded run and grounding already reads 1.0. The layer is structural: after this
change no fabricated quote can reach the output on ANY input, because an unverified
quote downgrades its check to indeterminate and is stripped from evidence before the
combinator runs — a verdict can only move toward UNVERIFIABLE.

**Change.** `assemble()` routes every model-sourced quote through
`verify_and_downgrade` (verify.py) and recomputes the verdict on the verified
outcomes; downgraded checks lose their evidence block and surface as
`evidence_unverified` in the uncertainty statement. One new test (fabricated quote →
UNVERIFIABLE); the four existing assemble tests gained the posting-source argument.

**Measurement.** Evidence: `eval/results/20260829-084751.json` — advanced identical
to the previous three runs on every metric (0.8 / 0.1429 / 1.0 grounding), fourth
consecutive identical result; no downgrades triggered on dev, as hypothesised.

**Verdict.** KEPT. No delta claimed; the change buys a guarantee, not a number.

**What this told me to do next.** Loop 3: the stance-extraction refinement for
case-26 — the last failure the pipeline can address inside its scope.

### [2] Non-A licence rating surfaces in the uncertainty statement
`4e43c41` · 2026-08-29 08:41 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** None on eval metrics — stated openly per BP-4: uncertainty text is
unscored. The change targets output honesty (End-to-End Quality): the B-rating
sub-check is cut by scope ruling, and case-28's output said "nothing material left
unresolved" about a B-rated sponsor that cannot issue a CoS until its action plan
completes.

**Change.** `src/advanced/solve.py::assemble` appends a rating caveat to the
uncertainty statement when the route-cited register row is not "(A rating)"; verdict
unchanged by design. Two new tests (non-A surfaces; A-rated stays quiet).

**Measurement.** Evidence: `eval/results/20260829-084140.json` — regression only:
advanced identical to `20260829-080609.json` on every metric (0.8 / 0.1429 / 1.0 /
0.975 / 1.0); case-28's uncertainty now reads "licence rating not assessed: the
register shows Worker (B rating); …". Baseline landed at 0.425 again, confirming the
widened single-prompt spread noted in REPRODUCTION.md §6.

**Verdict.** KEPT. No delta claimed; none expected. The verdict on case-28 remains
confidently wrong — that is the recorded price of the B-rating cut, now stated in the
output itself rather than hidden.

**What this told me to do next.** Loop 2: wire the verifier (the safety layer earns
its keep outside dev conditions); loop 3: the stance-extraction improvement for
case-26.

### [1] Extract → Resolve → Decide pipeline wired end to end
`f94da46` · 2026-08-29 08:06 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** Splitting the baseline's single judgment call into one extraction call
plus deterministic resolution and rules would eliminate the resolution and threshold
failure classes (docs/PLAN.md §3 failures 2, 3, 5, 8): verdict_utility above both
reference lines, confident_wrong_rate down, grounding at 1.0 — because code reads the
Route column and floor_config, and a model no longer aggregates its own checks.

**Change.** `src/advanced/`: `extract.py` (prompt builder + typed parser; the only
model call), `resolve.py` (normalisation + token-subset matching + alias fixtures;
`GENERIC_TERM_ORG_LIMIT` counts distinct orgs, matched-entity rows uncapped),
`rules.py` (thresholds from floor_config, pure combinator), `solve.py` (wiring +
pure `assemble`). Verifier unit-green, wired in the evening pass. 27 new tests.

**Measurement.** Evidence: `eval/results/20260829-080609.json`

| Metric | baseline (same run) | advanced | Delta |
|---|---|---|---|
| verdict_utility | 0.325 | 0.8 | **+0.475** |
| confident_wrong_rate | 0.4 | 0.1429 | −0.257 |
| decisive_accuracy | 0.6 | 0.8571 | +0.257 |
| decisive_rate | 0.8462 | 1.0 | +0.154 |
| check_accuracy | 0.8125 | 0.975 | +0.163 |
| grounding_rate | 0.951 | 1.0 | +0.049 |
| cost_per_case_usd | 0.01115 | 0.00298 | −73% |
| p50_seconds | 10.08 | 2.23 | −78% |

Against the frozen reference run (`20260829-002858.json`, baseline 0.225) the delta is
+0.575; against the same-run baseline above, +0.475. The noise floor is stdev 0.049 on
verdict_utility (`20260829-002003.json`), so the conservative delta is ~10σ. The
same-run baseline's 0.325 sits at the top of its measured range (0.225–0.325) —
consistent with noise, stated for honesty.

**Verdict.** KEPT. The pre-registered target (DECISIONS.md 2026-08-29) is met: beats
the baseline on verdict_utility (0.8 > 0.325) AND always_abstain on decisive_rate
(1.0 > 0) while decisive_accuracy rose (0.857 vs 0.6) — the gain is not abstention
drift; the advanced variant answers every determinable case and abstains on 6 of 7
truly unverifiable ones.

**What this told me to do next.** 18/20; the two remaining wrong verdicts are exactly
diagnosable, which is the pipeline's point. case-26: the extraction model classified
right-to-work boilerplate as "refused" — a stance-extraction error, the evening's
first measured improvement candidate. case-28: all four checks pass because nothing
reads the licence rating — the deliberately cut B-rating sub-check's price, one
confident-wrong; per the cut ruling the rating must at least surface in the
uncertainty statement, which it currently does not. Evening order: wire the verifier,
then one measured improvement per prompts/02 loop.

### [0] Baseline frozen
`cde01b2` · 2026-08-29 00:28 UTC · trajectory: `trajectories/2026-08-28-1833-prompt01-cases-and-baseline.md`

**Change.** Deliberately simple reference implementation in `src/baseline/solve.py`: one
pinned-model call (`claude-sonnet-4-6`, temperature 0.0) carrying the pasted requisition
plus a naive register lookup (most-specific name candidate wins; generic words skipped;
blindness to trading names, routes and ratings preserved by design). The prompt is basic
instructions only — four plain-language questions, the floor figures as data, the output
contract; no reason vocabulary, no threshold-combination rule, no pay-composition rule.
It is a faithful reproduction of the manual process in use today (README, "Baseline
solution"). **Frozen from commit `cde01b2` onward per CN-3 — never edited again. Every
later delta is measured against this exact file.**

Two superseded runs are part of the record, not the baseline: `eval/results/20260828-224144.json`
(a lookup defect delivered unrelated register rows on 5 of 20 dev cases — numbers
depressed, unfair as a reference; DECISIONS.md 2026-08-29) and `eval/results/20260829-002446.json`
(same numbers, dirty-tree flag; superseded by the clean rerun below).

**Measurement.** Evidence: `eval/results/20260829-002858.json` (reference table, clean
tree, seed 42, dev split). Noise floor: `eval/results/20260829-002003.json` (`--repeats 5`).

| Metric | baseline | always_abstain | advanced |
|---|---|---|---|
| verdict_utility | 0.225 | 0.5125 | — (stub) |
| confident_wrong_rate | 0.4667 | 0 | — |
| decisive_accuracy | 0.5333 | 0 | — |
| decisive_rate | 0.8462 | 0 | — |
| check_accuracy | 0.8 | 0 | — |
| grounding_rate | 0.99 | 0 | — |
| cost_per_case_usd | 0.01123 | 0 | — |
| error_rate | 0 | 0 | 1.0 (empty slot by design) |
| p50_seconds | 9.814 | ~0 | — |

Run-to-run noise (5 repeats, same seed): verdict_utility mean 0.265, stdev 0.04899
(range 0.225–0.325); confident_wrong_rate mean 0.44, stdev 0.03266; check_accuracy mean
0.8075, stdev 0.02031; grounding_rate mean 0.9644, stdev 0.007984; decisive_rate stdev 0.
**A verdict_utility delta smaller than ~0.1 (2σ) is noise, not a result.**

**What this told me to do next.** The baseline is decisive (84.6% of determinable cases
answered), well-grounded (0.99), and wrong on 46.7% of its definitive verdicts — its
utility sits 0.29 *below* trivial abstention. The failure is judgment, not retrieval:
route conflation (case-07 reads "Worker (A rating)" as route coverage while the Route
column says GBM), threshold aggregation (case-11's own failing salary check waved
through to SPONSORABLE), stance misreads (cases 20, 26), and name resolution (01, 04,
06 — case-04 is the only SPONSORABLE lost to it). Saturday builds exactly those stages:
extract → resolve (alias layer in scope) → rules engine reading `floor_config` — no
threshold or route logic in any prompt — with a measured dev-split run by midday; the
verifier in the evening; the report renderer Sunday morning. B-rating sub-check cut to
the uncertainty statement. Success target pre-registered in DECISIONS.md 2026-08-29:
beat the baseline on verdict_utility AND always_abstain on decisive_rate while holding
decisive_accuracy high.

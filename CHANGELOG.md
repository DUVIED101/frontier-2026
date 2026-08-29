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

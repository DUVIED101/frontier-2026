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
`<sha>` · TODO · trajectory: `trajectories/TODO.md`

**Change.** Deliberately simple reference implementation in `src/baseline/`. Frozen from this
commit onward per CN-3 — never edited again, so every later delta is measured against a fixed
point.

**Measurement.** Evidence: `eval/results/TODO.json`

| Metric | Baseline |
|---|---|
| TODO | TODO |

**What this told me to do next.** TODO

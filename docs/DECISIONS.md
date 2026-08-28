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

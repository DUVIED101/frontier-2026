# Prompt 01 — Build and freeze the baseline (Friday evening)

> **Ordering superseded (2026-08-28).** This file predates the approved plan; its
> sequence is replaced by `docs/PLAN.md` §8 (cases → fixtures → metrics → baseline). It
> is kept for its discipline — TDD, gates, freeze, changelog, trajectory — not its
> sequence. The executed sequence and the human gates are recorded in
> `trajectories/2026-08-28-1833-prompt01-cases-and-baseline.md`.

QNEW. Read CLAUDE.md.

Implement the approved baseline in `src/baseline/solve.py`.

Constraints:
- Simplest thing that works. No cleverness, no retries, no tuning, no optimisation.
  It exists to be beaten and it must fail visibly on the failure surface we identified.
- Failing test first, then implement (C-1).
- Seed every random source (C-6). The run must be deterministic.
- No dependency without a justification in the commit body (C-9).

Then:
1. Write 3–5 evaluation cases into `eval/cases/` as JSON. `expected` must be derived
   independently — never from the output of the code (T-7).
2. Add the agreed problem-specific metrics to `eval/metrics.py`. Keep the four generic ones.
3. Wire `load_cases()` and the variant runners in `eval/run_eval.py` if the case shape
   requires it. Do not restructure the harness.
4. Run: `python eval/run_eval.py --variant baseline --seed 42 --tag baseline-frozen`
5. Run it again with `--repeats 5` and report run-to-run variance. I need to know the noise
   floor before any improvement is claimed.

Report the metric table. Then write the `[0] Baseline frozen` entry in CHANGELOG.md citing
the results filename, and the trajectory file for this session.

After this commit, `src/baseline/` is frozen (CN-3). Confirm you understand that.

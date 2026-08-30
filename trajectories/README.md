# Trajectories

Representative session records for every agent used, per the submission package.

**Naming:** `YYYY-MM-DD-HHMM-<slug>.md`, UTC, e.g. `2026-08-29-0930-baseline-scaffold.md`

**Rules (CLAUDE.md section 6):**

1. Start the file when the session starts. Never reconstruct afterwards.
2. Record every tool call and its response, including failures.
3. Keep retries and dead ends — they are the most informative content here.
4. Mark human checkpoints explicitly with `> HUMAN: approved / rejected / redirected`.
5. Redact secrets at capture time.
6. Close with what shipped, which metric moved, and what was discarded.

**Index**

| File | Task | Metric moved |
|---|---|---|
| `2026-08-28-1833-prompt01-cases-and-baseline.md` | Case schema + 30-case set (two HUMAN gates), register snapshot + fixtures, metrics, baseline built and frozen | Established the floors: baseline verdict_utility band 0.225–0.425 (5-repeat noise floor), trivial abstention ~0.5 by construction |
| `2026-08-29-0757-prompt02-pipeline-construction.md` | Advanced pipeline build, Saturday improvement loops, and the Sunday close (guard, collision sweep, QREPRO, final run, README) as post-close checkpoints 1–13 | verdict_utility 0.225–0.425 → 0.9375 full set (holdout 1.0); grounding_rate → 1.0; confident_wrong_rate 0.2609 → 0.0455 |

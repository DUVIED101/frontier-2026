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
| `2026-08-28-1833-prompt01-cases-and-baseline.md` | Case schema + case set (30 authored at two HUMAN gates; 32 final after CHANGELOG [10]/[11]), register snapshot + fixtures, metrics, baseline built and frozen | Established the floors: baseline verdict_utility band, later measured at 0.225–0.4773 across all committed runs (CHANGELOG [4]); trivial abstention ~0.5 by construction |
| `2026-08-29-0757-prompt02-pipeline-construction.md` | Advanced pipeline build, Saturday improvement loops, and the Sunday close (guard, collision sweep, QREPRO, final run, README) as post-close checkpoints 1–16 | verdict_utility from the 0.225–0.4773 baseline band to 0.9375 full set (holdout 1.0); grounding_rate → 1.0; confident_wrong_rate 0.2609 → 0.0455 |

**Why two trajectories, not three:**

- Prompt 00 ran in plan mode — no file writes, no tool calls, analysis only. Its
  output is `docs/PLAN.md` with the approval record and the four amendments. No
  trajectory exists because there was no session activity to record; writing one
  after the fact would be reconstruction, which rule 1 above forbids.
- Sunday's work continues inside the Saturday file as post-close checkpoints, per
  the TR-1 note recorded in that file's final close.

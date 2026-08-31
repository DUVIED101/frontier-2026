# Prompt 04 — Submission assembly (Sunday evening / Monday)

Assemble the final package. Nothing new gets built from this point.

## 1. README.md
Fill every TODO. Order is fixed by the submission package — do not reorder.
- Intended user, their bottleneck, why it matters. Concrete, one named role.
- Results table, sourced from a single named `eval/results/` file.
- Baseline and advanced described so a judge understands the difference without reading code.
- Agent setup table: agent, model, tools, instruction file. Disclosure is mandatory.
- Main failure mode — the honest one from prompt 03, not a soft one.
- Hot take — one opinionated paragraph earned from building this. Not a general view on AI.
- Pre-existing work — verify the list matches what the git history actually shows before kickoff.

## 2. CHANGELOG.md
Every meaningful iteration present, newest first, each citing its results file. Discarded
experiments included. Identify the entry that contributed most — it is called out in both
the README and the video.

## 3. REPRODUCTION.md
Every TODO filled with real output pasted from a real run, not paraphrased. Versions,
approximate runtime, approximate cost.

## 4. trajectories/
One file per session, index table in `trajectories/README.md` complete. Confirm the
retries and human checkpoints are still there and were not tidied away.

## 5. Final verification
```
git status                     # clean
python eval/run_eval.py --seed 42   # flag-less — all three variants (G-4, amended 2026-08-30)
```
Run once more from a fresh clone in a clean container. If it does not run there, nothing
else in this package matters.

## 6. Video script (max 5 minutes) — output as a timed script
- 0:00 the problem and the user
- 0:40 the baseline and what it fails at
- 1:20 one realistic execution end to end
- 3:00 the comparison table
- 3:40 the changelog, and the single change that contributed most
- 4:20 one experiment that was removed, and why
Write it to be read aloud at a normal pace. Time each section.

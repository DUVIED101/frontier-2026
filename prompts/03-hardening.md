# Prompt 03 — Hardening pass (Sunday morning)

You are a skeptical senior engineer trying to break this submission before the judges do.

Work through, in order, and fix or report each:

1. **Reproducibility.** Follow REPRODUCTION.md literally in a clean container, knowing
   nothing about the repo. Every step that is wrong, missing, or assumes context is a
   blocker — this is the qualification gate, not a nicety.
2. **Determinism.** Run the eval three times with the same seed. Any variation that is not
   documented model non-determinism is a bug. Find the unseeded source.
3. **Evidence integrity.** Every number in README.md and CHANGELOG.md — does a committed
   file in `eval/results/` contain exactly that number? List any that do not.
4. **Secrets.** `git log -p | grep -iE "key|token|secret|password|Bearer"` and inspect
   `.env.example`. Anything real found is a blocker.
5. **Effects.** Every consequential action gated behind `--allow-effects`, defaulting off
   (CN-6). Anything that touches the network, the filesystem outside the repo, or an external
   service unguarded is a blocker.
6. **Frozen baseline.** `git log --oneline -- src/baseline/` — one commit after the freeze,
   or explain it.
7. **Failure modes.** Adversarial inputs: empty, malformed, oversized, wrong type,
   boundary values. What breaks? The one that breaks worst goes into README's "main failure
   mode" — do not hide it, name it and say what fixing it would take.
8. **Gates.** G-1 to G-4 all green.

Report as a numbered list: BLOCKER / WARNING / OK, with file and line.

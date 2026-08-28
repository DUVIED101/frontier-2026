# Prompt 00 — Bootstrap (run this FIRST, right after the problem PDF drops)

Paste into a fresh Claude Code session in the repo root. Do not let it write code yet.

---

Read CLAUDE.md in full. Every MUST rule is binding for this entire project.

I have just received the problem statement for the micro1 Frontier Engineering Challenge.
It is at: <PATH TO PROBLEM PDF / pasted below>

<PASTE PROBLEM STATEMENT>

Do not write any code yet. Produce this analysis, and nothing else:

1. **Restatement.** The problem in your own words, in five sentences. If any part is
   ambiguous, say so — incomplete requirements are the stated theme of this challenge, so
   ambiguity is signal, not noise.

2. **Hard constraints.** Everything the statement prescribes: starter repo, runtime,
   dependency limits, API access, acceptance tests, output format. Quote the exact wording
   for each. These are non-negotiable and a violation is a disqualification.

3. **Acceptance criteria → tests.** Every stated criterion, one line each, with the name of
   the test that will verify it. If a criterion cannot be tested as written, say what
   interpretation you would test instead and flag it as an assumption.

4. **Intended user.** Who has this problem in reality. Name a specific role and a specific
   bottleneck. This becomes the opening of README.md and is judged.

5. **Failure surface.** The edge cases, hidden dependencies and failure modes a naive
   solution will miss. Rank them by how likely a judge is to test them. This list is where
   the baseline-to-advanced delta comes from, so be exhaustive rather than tidy.

6. **Baseline proposal.** The simplest implementation that could pass the stated criteria.
   It must be buildable in under 90 minutes and must obviously fail on items from (5).
   Say which items it will fail on.

7. **Advanced direction.** Two or three candidate approaches, each with: the mechanism, the
   metric it should move, the risk, and the time cost. Recommend one and state the cost of
   being wrong about it.

8. **Metrics.** The three to five metrics to add to eval/metrics.py. At least one must map
   to a stated acceptance criterion, and at least one must capture a failure mode the
   baseline exhibits. For each: name, definition, direction, and how it is computed cheaply
   and deterministically.

9. **Schedule.** Fit the above into: Fri evening = baseline green; Sat = advanced;
   Sun = eval, changelog, reproduction guide; Mon until 18:00 UTC = video and submit.
   Say what you would cut first if the schedule slips.

Wait for my approval before touching any file.

# Prompt 02 — Improvement loop (Saturday, repeat per iteration)

Run this once per improvement. One improvement per loop, never two.

---

QPLAN.

Current state: latest results in `eval/results/`. Read that file before planning.

Proposed improvement: <ONE SENTENCE>

Plan it against CLAUDE.md. Your plan must state:
- which metric this moves and in which direction
- the expected magnitude, and whether that magnitude exceeds the measured noise floor
- what it costs in time
- what would make you abandon it mid-way

Wait for approval.

---

After approval: QCODE. Implement in `src/advanced/` only. `src/baseline/` is frozen.

Then in order:
1. QCHECK — review your own change as a skeptical senior engineer.
2. QEVAL — run the harness on both variants.
3. Judge the delta honestly against the noise floor. **If it is inside the noise, say so and
   recommend reverting.** A reverted experiment is a changelog entry and video material; a
   fake improvement is a scoring risk under "connect every claim to the evidence".
4. QLOG — CHANGELOG entry citing the results file. Numbers must match it exactly.
5. QTRACE — trajectory file including the failures and retries.
6. QGIT.

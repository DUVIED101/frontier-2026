# Video script — 5:00 max, read aloud at normal pace

Screen directions in brackets. Word counts tuned to ~150 wpm. Every number spoken
here is in `eval/results/20260830-101148.json` or the file named in the section.

---

## 0:00 — The problem and the user (~40 s / ~100 words)

[Screen: a real job posting]

I'm an early-career software engineer in the UK. My visa depends on finding an
employer who can sponsor a Skilled Worker visa, and roles at my level close within
forty-eight hours. Whether any posting can actually sponsor me rests on four facts
in three different places: is the legal entity on the Home Office register — is the
licence for the Skilled Worker route, not an intra-company one — will they sponsor
*this* role — and does the salary clear the legal floor. Any one of them kills it.
The cost of getting it wrong isn't the application; it's the interviews that follow
— hours spent on a role that could never have ended in an offer.

## 0:40 — The baseline, and what it fails at (~40 s / ~100 words)

[Screen: terminal — `python eval/run_eval.py --variant baseline --split dev` output, then the baseline's answer on the hard case]

The baseline is my actual current process, automated literally: paste the posting
into a chat that has the register loaded, take the one-minute answer. Measured over
thirty-two labelled cases, that answer is confidently wrong on twenty-six percent
of its definitive verdicts, and about six percent of its citations don't survive
mechanical checking. On a live posting it invented a salary — quoted a market
estimate for a number the posting never states. Producing an answer was never the
bottleneck. Trusting it is.

## 1:20 — One realistic execution, end to end (~1 min 40 s / ~240 words)

[Screen: `python -m src.advanced.cli posting.txt` on the compound hard case — an aggregator posting, brand name only, whose legal entity holds a GBM-only licence]

One command, one posting. Two seconds, a third of a cent.

[Point at the report as each line is spoken]

The verdict comes first, with the one sentence that determines it. Then the four
checks, each with evidence I can check myself: the sponsorship quote carries
character offsets into the posting — byte-verbatim, or it doesn't count. The
register row is reproduced field-for-field from a committed snapshot of the real
Home Office register — a hundred and forty-three thousand rows. The snapshot date is
printed with a warning, because licences get revoked weekly and a verdict is only
as fresh as its snapshot. And when something can't be established, the report says
exactly what and exactly what I'd have to do about it — ask which legal entity
issues the Certificate, ask for the guaranteed basic salary in writing.

The architecture in one sentence: a model extracts typed claims, and deterministic
code does everything else — entity resolution against the register, a pure rules
engine with the floor as versioned data, mechanical verification of every quote
and row, a renderer with no model in it. Code decides; the model extracts. One
choice is worth naming: the verifier bought no measured improvement on our cases —
and stayed, because it bounds the direction of failure: unsupported evidence can
only move a verdict toward abstention, never toward confidence. This case is the
trap: the entity IS on the register, but the licence is the wrong route.
One-prompt tools say yes. This says NOT SPONSORABLE, and cites the row.

## 3:00 — The comparison (~40 s / ~100 words)

[Screen: the three-column table from eval/results/20260830-101148.md]

Full set, thirty-two cases, three columns — baseline, a trivial always-abstain
floor, and the pipeline. Verdict utility: point nine four against point five five,
and the floor at point four eight matters — always abstaining scores points, so
beating the baseline isn't enough. Confident-wrong: four and a half percent versus
twenty-six. Grounding: one hundred percent — every citation survives mechanical
verification. Three point six times cheaper, more than four times faster. And the ten
held-out cases, never opened during development: perfect on every metric —
that subset contains none of the class we fail on.

## 3:40 — The changelog, and the change that mattered most (~40 s / ~100 words)

[Screen: CHANGELOG.md, entry [1]]

Fifteen logged iterations, each citing its results file. The one that mattered
most was the first: wiring extraction, resolution and rules into a measured
pipeline — verdict utility went from a baseline band of point two two to point
four two, up to point eight, and the conservative delta is computed against the
band's best figure, never against whichever baseline landed in the same run.
Almost everything after was smaller — and half of it was honesty work: fixes for
places where an artifact contradicted a claim made about it. Every one of those
had passed a green test suite.

## 4:20 — The experiment that was removed (~35 s / ~90 words)

[Screen: CHANGELOG.md entry [5], the self-consistency table]

One experiment was removed, by its own numbers: self-consistency voting. It scored
*worse* than the single-shot baseline at three times the cost, because when a model
systematically substitutes world knowledge for evidence, sampling it three times
votes the same error in. That's the thesis of the whole project: you don't fix
ungrounded confidence by asking for it three times. You fix it by making code
decide, and letting the model do only what it's good at — reading.

[Screen: repo README]

Everything you just saw reproduces from a clean clone with one guide. Thanks.

## — total ≈ 4:55

**Production note:** read once against a stopwatch before recording. If it
overruns, cut from the 1:20 architecture sentence — never from the close.

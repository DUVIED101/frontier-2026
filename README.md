# frontier-2026

Entry for the **micro1 Frontier Engineering Challenge 2026** (28–31 August 2026).

> **Fill order:** this document is written last, but the headings are fixed now and follow the
> submission package exactly. Do not reorder them. Delete every `TODO` before submitting.

---

## The intended user

<!-- Who is this for, concretely. One person, one role, not "developers". -->
TODO

## Their current bottleneck

<!-- What they do today, why it is slow, wrong, expensive, or unreliable.
     Be specific enough that a judge who has never met this user can picture the failure. -->
TODO

## Why existing tools don't answer this

<!-- Prior art and the specific way each partial solution fails.
     Filled from the section of the same name in docs/PLAN.md. -->
TODO

## Why solving it is valuable

<!-- What changes for that user when this works. Quantify if the eval supports it. -->
TODO

---

## Results at a glance

| Metric | Baseline | Advanced | Delta |
|---|---|---|---|
| TODO | — | — | — |

Source of record: [`eval/results/TODO.json`](eval/results/)
Every number in this document comes from that file. Reproduce with
[`REPRODUCTION.md`](REPRODUCTION.md).

*Reading `grounding_rate` for `always_abstain`: it scores 0 because that variant
issues no citations at all — the metric verifies citations issued, and zero issued is
zero by construction, not fabrication. The meaningful grounding comparison is baseline
vs advanced.*

---

## Baseline solution

<!-- The deliberately simple approach. What it does, what it cannot do. -->
Located in `src/baseline/`. Frozen after its first green run and never modified since —
it is the measurement reference, not a fallback implementation.

The baseline is not a straw man; it is a faithful reproduction of the manual process in
use today. The author's actual current workflow for this problem is to paste the
requisition into a chat session that already has the sponsor register loaded and take
the one-minute answer — which is exactly what `src/baseline/solve.py` implements: one
direct prompt with basic instructions and a naive name lookup over the same committed
register snapshot. The challenge brief lists "the manual process people use today" as a
legitimate baseline; this one qualifies literally rather than by analogy.

TODO — fill measured failure profile from the frozen-baseline results file.

## Advanced solution

<!-- The real submission. Architecture, the key mechanism, why it beats the baseline. -->
Located in `src/advanced/`.

Two findings to carry into the final text (recorded 2026-08-29):

**Determinism is a measured property here, not a claim.** The baseline — one model
call that judges everything — produced three different verdict_utility values across
committed runs (0.225, 0.325, 0.425). The advanced pipeline produced *identical*
numbers across five independent runs, including one from a fresh clone, and then
moved by exactly the hypothesised +0.10 when its one prompt was deliberately changed.
Replacing model judgment with deterministic stages removed the run-to-run variance the
baseline still has; the only remaining model surface is one small extraction call.

**The verifier bought no measured improvement on this case set, and stays.** Stated
exactly that way: extraction quotes were already verbatim in every recorded run, so
wiring the verifier moved nothing (`eval/results/20260829-084751.json`). It remains
because it bounds the direction of failure — fabricated evidence can only move a
verdict toward UNVERIFIABLE, never toward confidence. It is a guarantee, not a
performance component, and claiming otherwise would be the kind of unbacked claim
this repo's evidence chain exists to prevent.

TODO — architecture narrative and final full-set numbers, filled Sunday.

---

## Agent setup

Coding-agent use is required by the challenge and disclosed in full here.

| Agent | Model | Tools granted | Instruction file |
|---|---|---|---|
| TODO | TODO | TODO | [`CLAUDE.md`](CLAUDE.md) |

Full instruction set: [`CLAUDE.md`](CLAUDE.md) and [`prompts/`](prompts/).
Session records: [`trajectories/`](trajectories/).

---

## Improvement Changelog

Full log with evidence per entry: [`CHANGELOG.md`](CHANGELOG.md).

Summary of the iteration that mattered most:

TODO

---

## Reproduction

See [`REPRODUCTION.md`](REPRODUCTION.md). Written for a clean environment with exact
commands for the solution, the baseline, and the evaluation.

The guide was verified a day early — executed literally, command by command, from a
fresh clone on Saturday rather than trusted until Sunday. That verification is why it
can be trusted at all: the "recommended" Docker path turned out never to have built
(a copy path wrong for its build context), and, with no `.dockerignore`, would have
baked `.env` — the API key — into an image layer. Both were found only because the
path was actually exercised, and both are fixed and re-verified (build, full test
suite and eval harness confirmed in-container).

---

## Main failure mode

<!-- Where this breaks. Judges reward the honest answer, not the absence of one.
     Name the specific input class that defeats it and say what it would take to fix. -->
TODO

**Known evaluation limitation (recorded 2026-08-29, DECISIONS.md).** The highest-harm
failure mode in the design — world-knowledge substitution, where a model asserts a
household-name employer "obviously" sponsors without a register row — is one this
evaluation structurally cannot elicit: every employer in the fixtures is fictional, so
no model holds a prior about any of them. Case-01 was designed to trigger that failure
and cannot at verdict level; it discriminates at check level instead (which evidence
chain produced the verdict). The failure mode is real in production use on real
employers; measuring it would require real-brand cases, which the synthetic-fixture
decision (CN-7) deliberately traded away.

## Hot take

<!-- One opinionated paragraph. Earned from building this, not a general position on AI. -->
TODO — write Sunday. Earned candidates, recorded as they happened:
- An untested path that looks correct is not evidence — the difference is
  verification. This repo's own reproduction guide recommended a Docker path that had
  never built and would have leaked the API key into an image layer; it was caught
  only by executing the guide literally. The same thesis the solution applies to job
  postings applied to the project itself.
- The strong baseline prompt was answering its own exam: handing the model the
  thresholds, the reason vocabulary and the combination rules measured the author's
  research, not the model's judgment. A fair baseline had to be weakened back to what
  a person actually types.
- Three times in one day the pipeline knew something its surface lost — a licence
  rating, the candidate entities behind an ambiguity, a line-wrapped quote — and all
  three were found by reading output, not metrics. An eval can only measure the
  failure modes its fixtures contain, and every fixture set shares properties with
  its author rather than with the world: twenty hand-written cases all kept their
  quotable sentences on one line, and the first real pasted posting did not.

---

## Pre-existing work

Declared per the Rule Book requirement to make clear what existed before the competition and
what was added during it.

**Created before kickoff (16:00 London, 28 August 2026), visible in the git history:**

- Repository scaffold and directory layout
- `CLAUDE.md` — agent operating rules, containing no domain or problem-specific content
- Evaluation harness skeleton (`eval/run_eval.py`, `eval/metrics.py`) with no metrics defined
- Documentation templates: this file, `REPRODUCTION.md`, `CHANGELOG.md`
- Pinned Docker runtimes for Python and Node
- Reusable agent prompt templates in `prompts/`

No part of the problem statement was known at that point, and no solution logic exists in any
pre-kickoff commit. Every commit is timestamped and the history has not been rewritten.

**Third-party dependencies:** listed with exact pinned versions in `docker/requirements.txt`
and `package.json`. Each is used under its own licence.

**Data:** provenance and licensing in [`docs/DATA.md`](docs/DATA.md).

---

## Licence

TODO — pick before submitting. Submissions are governed by the Hackathon Participation
Agreement accepted at registration.

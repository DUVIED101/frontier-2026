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

---

## Baseline solution

<!-- The deliberately simple approach. What it does, what it cannot do. -->
Located in `src/baseline/`. Frozen after its first green run and never modified since —
it is the measurement reference, not a fallback implementation.

TODO

## Advanced solution

<!-- The real submission. Architecture, the key mechanism, why it beats the baseline. -->
Located in `src/advanced/`.

TODO

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

---

## Main failure mode

<!-- Where this breaks. Judges reward the honest answer, not the absence of one.
     Name the specific input class that defeats it and say what it would take to fix. -->
TODO

## Hot take

<!-- One opinionated paragraph. Earned from building this, not a general position on AI. -->
TODO

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

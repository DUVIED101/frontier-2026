# frontier-2026

Entry for the **micro1 Frontier Engineering Challenge 2026** (28–31 August 2026).

**What it is:** paste a UK job requisition; get **SPONSORABLE / NOT SPONSORABLE /
UNVERIFIABLE** for a Skilled Worker visa, as a plain-English verification report in
which every claim carries evidence a person can check — a byte-verbatim quote with
character offsets into the posting, or a register row reproduced from a committed
snapshot. Code decides; the model only extracts.

```bash
python -m src.advanced.cli path/to/posting.txt
```

---

## The intended user

An early-career software engineer already working in the UK who needs Skilled Worker
sponsorship to stay, applying against a visa deadline in a market where roles at their
level close within 48 hours. One person with a countdown, not "developers".

## Their current bottleneck

Whether a requisition is viable rests on four independent facts that live in three
different places: the hiring **legal entity** is on the Home Office sponsor register
(published under registered names, while postings use trading names); that entity's
licence covers the **Skilled Worker route** specifically (a Global Business
Mobility-only licence is an intra-company route this user cannot use); the employer is
**willing** to sponsor *this* role (holding a licence and using it are different
facts); and the advertised **salary** clears the applicable floor (£38,300, SOC 2134
new-entrant, versioned in `floor_config.json`). Any single failed check kills the
application, and the checks fail independently.

What this user does today — the author's actual process, stated as such — is paste the
requisition into a chat session that already has the register loaded and take the
one-minute answer. Producing an answer was never the bottleneck; **trusting it is**.
Measured on this repo's own evaluation, that one-minute answer is confidently wrong on
26% of its definitive verdicts and ~6% of its citations fail mechanical verification
— so acting on it means re-deriving it against the register by hand, which costs more
than the answer did. The honest metric is time-to-a-trustworthy-answer: time until
the user can act, *including* the time to verify or refute what the tool claimed.

## Why solving it is valuable

The application form is the cheap part of getting this wrong. A false SPONSORABLE
sends hours — screening call, recruiter conversation, technical interview — into a
pipeline that cannot end in an offer. A false NOT SPONSORABLE silently discards a
viable role, and the user never learns it existed. An honest UNVERIFIABLE costs one
question to the employer. The scarce resource is attention under a deadline, and the
error costs are asymmetric — which the primary metric (`verdict_utility`) encodes: a
confident wrong verdict scores 1.25 points below an honest abstention.

Measured (all numbers from the final run, `eval/results/20260830-101148.json`): the
advanced pipeline cut confident-wrong from 26% to 4.5% of definitive verdicts, took
citation grounding from 93.7% to 100%, answers in ~2 s at $0.0031/case, and on the
one live timed case where the manual process went wrong it returned a grounded
answer in 7 s where the manual process took 130 s *and substituted a market estimate
for a salary the posting never states* (docs/TIMING.md, measurement 1).

## Why existing tools don't answer this

Job-board sponsorship filters answer "does the posting mention sponsorship", not "can
this requisition produce a Certificate of Sponsorship". In the author's own search, a
scrape of ~400 mid-level London software roles over six months returned **2** rows
flagged as mentioning sponsorship — employers who sponsor overwhelmingly say nothing,
so the filter's negatives are meaningless. Register lookup tools answer presence
only: a Global Business Mobility-only licence reads as a positive, which is the most
expensive failure because it produces a confident false SPONSORABLE. Nothing checks
willingness at the requisition level — licensed, A-rated employers routinely publish
roles stating they cannot sponsor. Nothing applies the salary floor as a
disqualifier. The four checks are individually available and never composed — and
the composition is where the two-hop failures live, which is what the compound hard
case in the evaluation demonstrates (aggregator posting, brand name, GBM-only
licence: two failures in sequence, both pushing toward false SPONSORABLE).

---

## Results at a glance

Final run of record: all 32 cases (22 dev / 10 held-out), all three variants, one
flag-less command, clean tree (`git_dirty: false` in the file).

| Metric | Baseline | Trivial abstention | Advanced |
|---|---|---|---|
| verdict_utility (primary) | 0.5547 | 0.4844 | **0.9375** |
| confident_wrong_rate | 0.2609 | 0 | **0.0455** |
| decisive_accuracy | 0.7391 | 0 | **0.9545** |
| decisive_rate | 0.8636 | 0 | **1.0** |
| check_accuracy | 0.8125 | 0 | **0.9922** |
| grounding_rate | 0.9371 | 0 | **1.0** |
| cost_per_case_usd | 0.0112 | 0 | **0.0031** |
| exact_match | 0 | 0 | **0.9688** |
| p50_seconds | 9.7 | ~0 | **2.1** |

Source of record: [`eval/results/20260830-101148.json`](eval/results/20260830-101148.json) ·
dev/holdout breakdown: [`eval/results/final-breakdown-2026-08-30.md`](eval/results/final-breakdown-2026-08-30.md) ·
reproduce with [`REPRODUCTION.md`](REPRODUCTION.md).

**The held-out 10 cases — never opened during development — scored perfect:**
verdict_utility 1.0, confident_wrong 0, check_accuracy 1.0, grounding 1.0,
exact_match 1.0. The one imperfection in the full set is dev case-28, a deliberately
priced design cut (a licence-rating sub-check folded into the uncertainty statement
instead of the verdict; the report carries the caveat). Stated against that: the
holdout was *easier for the baseline at verdict level and harder at check level* —
its verdict_utility rose (0.725 vs 0.4773 dev) while its evidence quality fell
(check_accuracy 0.75 vs 0.8409; grounding 0.9149 vs 0.9464), so its extra right
answers rest on worse evidence chains. The honest comparison is the full-set delta
of +0.38, and the conservative dev-band comparison in
[`CHANGELOG.md`](CHANGELOG.md) entry [1].

*Reading `grounding_rate` for the trivial-abstention floor: it scores 0 because that
variant issues no citations at all — the metric verifies citations issued, and zero
issued is zero by construction, not fabrication. The meaningful grounding comparison
is baseline vs advanced.*

*Denominators changed during Saturday's hardening, and the honest version is stronger
than pretending otherwise: cases 31 (line-wrapped quote) and 32 (multi-route entity)
were added after live inputs exposed shapes no fixture had, moving the dev split from
20 to 22 cases and the abstention floor from 0.5125 to ~0.489 — and case-31 pulled
the baseline's grounding down, because its unwrapped quote does not ground either.
Both are the fixture set becoming slightly more like the world and slightly less like
its author. Aggregates across different denominators are not directly comparable; the
per-case verdicts are what carry across the change.*

*Before the final run, every case's employer strings were mechanically re-resolved
against the committed snapshot: all 32 resolve for their labelled reasons; the two
ambiguity cases surface real register namesakes alongside the designed fixtures
(11 and 3 candidates), measured and recorded rather than engineered away
([`eval/results/collision-sweep-2026-08-30.md`](eval/results/collision-sweep-2026-08-30.md)).*

---

## Baseline solution

Located in `src/baseline/`. Frozen after its first green run and never modified since —
it is the measurement reference, not a fallback implementation.

The baseline is not a straw man; it is a faithful reproduction of the manual process in
use today. The author's actual current workflow for this problem is to paste the
requisition into a chat session that already has the sponsor register loaded and take
the one-minute answer — which is exactly what `src/baseline/solve.py` implements: one
direct prompt with basic instructions and a naive name lookup over the same committed
register snapshot. The challenge brief lists "the manual process people use today" as a
legitimate baseline; this one qualifies literally rather than by analogy.

Fairness required weakening it once: the first baseline prompt handed the model the
salary thresholds, the reason vocabulary and the combination rules — it was answering
its own exam, measuring the author's research rather than the model's judgment. It was
rolled back to what a person actually types, and the change is recorded with numbers in
`CHANGELOG.md` and `docs/DECISIONS.md`.

**Measured failure profile** (final run, baseline column): confidently wrong on 26% of
its definitive verdicts; 6.3% of citations fail mechanical verification (fabricated or
paraphrased quotes, rows not in the snapshot); verdict_utility unstable across
identical invocations — committed n=20 runs produced three distinct values (0.225 /
0.325 / 0.425, including a 5-repeat noise floor) because single-prompt judgment flips
on borderline cases; exact_match 0 — it never produces a
fully label-consistent evidence chain, even when its verdict is right. On live input it
exhibited the designed failure mode 1: substituting a market estimate for a salary the
posting does not state (docs/TIMING.md).

## Advanced solution

Located in `src/advanced/`. Binding principle throughout: **code decides, the model
extracts** — a model is never the last thing between evidence and a verdict.

One pipeline, five stages, one model call:

1. **Extract** (`extract.py`) — the only model call (claude-sonnet-4-6, temperature
   0.0, pinned): typed claims out of the posting — employer names as stated, salary
   structure with guaranteed-basic bounds, sponsorship stance with a verbatim quote.
   Parsed into typed dataclasses; typed errors, no silent fallbacks.
2. **Resolve** (`resolve.py`) — deterministic entity resolution against the committed
   142,988-row register snapshot: exact-normalised match over every posting-stated
   string, then token-subset, then the alias fixtures — the posting's own words
   outrank external fixtures, and the winning phase names the register reason. More
   than one surviving entity is `Ambiguous`, never a guess.
3. **Rules** (`rules.py`) — pure functions. Salary thresholds come from
   `floor_config.json`, never from a prompt or a code literal; the verdict comes from
   a combinator over the four check outcomes, never from a model.
4. **Verify** (`verify.py`) — mechanical gates: every quote must appear byte-verbatim
   in the source, every cited register row must exist in the snapshot. Anything
   unsupported is downgraded toward UNVERIFIABLE — fabricated evidence can move a
   verdict only toward abstention, never toward confidence.
5. **Render** (`report.py`) — a pure renderer, no LLM: verdict, the sentence that
   determines it, each check with its offset-anchored evidence, the snapshot date
   with an age warning, and an uncertainty section naming what could not be
   established and what the user would have to do to establish it.

Two findings worth more than the architecture:

**Determinism is a measured property here, not a claim.** The baseline — one model
call that judges everything — produced three different verdict_utility values across
committed runs. The advanced pipeline has produced *identical* verdict-level numbers
across every independent run at every case-set size, including from a fresh clone on
each of two days, and moved by exactly the hypothesised amount when its one prompt was
deliberately changed. Replacing model judgment with deterministic stages removed the
run-to-run variance; the only remaining model surface is one small extraction call.

**The verifier bought no measured improvement on this case set, and stays.** Stated
exactly that way: extraction quotes were already verbatim in every recorded run, so
wiring the verifier moved nothing (`eval/results/20260829-084751.json`). It remains
because it bounds the direction of failure — and the wrapped-quote defect it later
surfaced on live input (CHANGELOG [10]) is precisely the class it exists to catch. It
is a guarantee, not a performance component.

---

## Agent setup

Coding-agent use is required by the challenge and disclosed in full here. This project
was built end-to-end through a coding agent operating under a written contract.

| Agent | Model | Tools granted | Instruction file |
|---|---|---|---|
| Claude Code (CLI), operator-gated | claude-fable-5 (agent sessions); claude-sonnet-4-6 pinned for both solver variants | File read/edit, bash, git; Anthropic API via `ANTHROPIC_API_KEY` (workspace-scoped env var, never committed) | [`CLAUDE.md`](CLAUDE.md) + [`prompts/`](prompts/) |

Every session is captured live in [`trajectories/`](trajectories/) — tool calls,
failures, retries, and every human gate marked `> HUMAN: approved / rejected /
redirected` with the reason. The operator reviewed plans before implementation,
reviewed diffs after, and issued the corrections the trajectory records; the agent
wrote the code, ran the gates, and was required to connect every claim to a committed
evidence file before writing it down.

---

## Improvement Changelog

Full log with evidence per entry: [`CHANGELOG.md`](CHANGELOG.md).

The iteration that mattered most was the first one: wiring extract → resolve → rules
into a measured pipeline took verdict_utility to 0.8 against a baseline band of
0.225–0.425 (entry [1]); the Saturday loops carried it to 0.9091 on dev, with the
conservative delta always computed against the band's best figure — **+0.475** at
minimum — never against whichever baseline landed in the same run (entry [4]
appendix). Everything after was smaller and half of it was honesty work: a verifier
kept despite moving nothing (entry [3]), a self-consistency experiment rejected by
its own numbers at 3× the cost (entry [5]), and five separate fixes for places where
an artifact contradicted a claim made about it (entries [7]–[12]).

---

## Reproduction

See [`REPRODUCTION.md`](REPRODUCTION.md). Written for a clean environment with exact
commands for the solution, the baseline, and the evaluation; executed literally from a
fresh clone on both 2026-08-29 and 2026-08-30 (101 tests, both eval paths, the demo
CLI, and the documented run-to-run variance behaving as documented).

The guide was verified a day early — executed literally, command by command, from a
fresh clone on Saturday rather than trusted until Sunday. That verification is why it
can be trusted at all: the "recommended" Docker path turned out never to have built
(a copy path wrong for its build context), and, with no `.dockerignore`, would have
baked `.env` — the API key — into an image layer. Both were found only because the
path was actually exercised, and both are fixed and re-verified (build, full test
suite and eval harness confirmed in-container).

The numbers are guarded mechanically as well as by rule: the harness refuses to start
a tagged run from a dirty working tree (the refusal prints before any model call), and
no number reaches this document from a results file whose `git_dirty` field is true.

---

## Main failure mode

The honest one, named: **a trading name the resolver cannot reach**. Entity resolution
is deterministic — exact match, token-subset, then a committed alias table. A posting
that names its employer only by a brand absent from all three (no shared tokens with
the registered name, no alias fixture) resolves NoMatch, and NoMatch after the full
alias pass is a definitive register fail: a licensed employer read as unlicensed, a
viable role silently discarded — the failure class the user never gets to notice. The
fix is a live Companies House lookup at resolve time; it was deliberately cut at
planning (the eval never touches the network, CN-7/CN-6), and the alias fixtures stand
in for it. The UNVERIFIABLE-inflation risk of widening resolution was the watched
alternative; the recorded choice and its reasoning are in `docs/DECISIONS.md`.

**Known evaluation limitation (recorded 2026-08-29, DECISIONS.md).** The highest-harm
failure mode in the design — world-knowledge substitution, where a model asserts a
household-name employer "obviously" sponsors without a register row — is one this
evaluation structurally cannot elicit: every employer in the fixtures is fictional, so
no model holds a prior about any of them. Case-01 was designed to trigger that failure
and cannot at verdict level; it discriminates at check level instead (which evidence
chain produced the verdict). The failure mode is real in production use on real
employers; measuring it would require real-brand cases, which the synthetic-fixture
decision (CN-7) deliberately traded away. It has since been observed live exactly as
designed: on a real posting the baseline substituted a market estimate for a salary
the posting does not state, while the pipeline returned indeterminate and quoted the
text (docs/TIMING.md, measurement 1).

## Hot take

The invariance script is the hot take. It was written to *prove* something — that a
data-file rebuild had changed no solver input — and its own first run showed its claim
was too strong: "identical inputs" had to be weakened to "identical content, orderings
disclosed" before the proof would pass. That was the fifth time in two days a claim
about an artifact was contradicted by the artifact itself — a solver disclosure that
never reached the report, ambiguity candidates hidden from the user, a line-wrapped
quote failing byte-verbatim verification, a manifest describing sort positions its own
file did not have — and a sixth (a data guide asserting a case count two smaller than
the case directory) followed within hours and became a test. **Every one of them
passed a green test suite.** A test suite verifies the properties someone thought to
encode; it is silent on every claim made *about* the artifact elsewhere — in
manifests, in guides, in the checker itself. The discipline this project sells — no
claim without the artifact to back it — is worth anything only if it is also applied
to the instruments doing the checking, and the moment the checking instrument caught
itself was the best evidence all weekend that it was.

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

**Third-party dependencies:** listed with exact pinned versions in
`docker/requirements.txt` — one runtime dependency (`anthropic`) plus the dev
toolchain (`pytest`, `mypy`, `ruff`). Each is used under its own licence. The Node
scaffold is unused — the solution is Python-only.

**Data:** provenance and licensing in [`docs/DATA.md`](docs/DATA.md).

---

## Licence

Code and synthetic fixtures: MIT (see [`LICENSE`](LICENSE)). The register snapshot
remains © Crown copyright, used and redistributed under the Open Government Licence
v3.0 — provenance in [`docs/DATA.md`](docs/DATA.md). Submissions are governed by the
Hackathon Participation Agreement accepted at registration.

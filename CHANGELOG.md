# Improvement Changelog

One entry per meaningful iteration, newest first. Each entry is connected to the evidence
that guided the next decision, per the submission requirements.

**Rules for every entry:**
- Numbers must match the cited `eval/results/` file exactly. If there is no file, there is no claim.
- Record what the evidence made you do next. That link is the point of the document.
- Discarded experiments get entries too. The solution video explicitly asks for one experiment
  that was removed — this is where it comes from.

---

## Entry template — copy this, do not improvise

```markdown
### [N] <short imperative title>
`<commit sha>` · <YYYY-MM-DD HH:MM> · trajectory: `trajectories/<file>.md`

**Hypothesis.** What was expected to improve, and why that was a reasonable guess.

**Change.** What was actually built. Files touched.

**Measurement.** Evidence: `eval/results/<file>.json`

| Metric | Before | After | Delta |
|---|---|---|---|
| | | | |

**Verdict.** KEPT / REVERTED / PARTIAL — and the reason, in the numbers.
Is the delta larger than run-to-run variance? State the variance.

**What this told me to do next.** The decision the evidence forced.
```

---

## Log

### [15] Empty posting is UNVERIFIABLE, not a register fail
`63546d0` · 2026-08-30 10:54 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** No dev metric movement — no dev case states no employer. Prompt 03
adversarial pass finding: an empty posting produced a confident NOT_SPONSORABLE,
because `NoMatch` with nothing searched carried the same definitive weight as a
confirmed absence. C1's "NoMatch after the full alias pass is definitive"
presupposes an employer was stated; with none, there is no absence claim to make —
and a confident wrong NOT_SPONSORABLE from degenerate input is the class-B failure
(silently discarded role) pointed at nothing. Second finding, same pass: a binary
file surfaced a raw UnicodeDecodeError traceback from the CLI.

**Change.** `_register_check`: NoMatch with no non-empty searched string is
`indeterminate/no_employer_stated`, with its own action line in the report
("identify the employing legal entity first…"). CLI: undecodable input exits 2
with a typed message before any model call. Both red-first
(`test_no_stated_employer_is_not_a_register_fail`,
`test_cli_rejects_a_non_text_file_without_calling_the_model`).

**Measurement.** Evidence: `eval/results/20260830-105501.json` — advanced identical
on every metric (verdict_utility 0.9091, check_accuracy 0.9886, grounding 1.0,
exact_match 0.9545), as hypothesised. Live re-fire: empty file renders UNVERIFIABLE
with all four checks unresolved; binary file exits 2 cleanly.

**Verdict.** KEPT. Found by the hardening pass's adversarial step, not by the
fixture set — the same lesson as cases 31 and 32: the eval measures the failure
modes its fixtures contain, and boundary inputs live outside them.

### [14] Ambiguity note grouped by licence route
`8438913` · 2026-08-30 10:35 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** No metric movement — note layer only, and `eval/metrics.py` never
reads `uncertainty_notes`. Operator-queued presentation fix, unblocked by the
collision sweep validating the resolution it presents: case-24's ambiguity
genuinely surfaces eleven candidates, and enumerating each entity with its routes
buried the one split the user actually weighs.

**Change.** `assemble` groups ambiguity candidates under their licence route
(largest group first, all entities still named); failing test first
(`test_ambiguity_note_groups_candidates_by_licence_route`, exact-string assertion).
Case-24 now reads: "11 register entities match the posted employer. By licence
route — Skilled Worker: [ten names]; Global Business Mobility: Senior or
Specialist Worker: Halcyon Consulting (UK) Ltd."

**Measurement.** Evidence: `eval/results/20260830-103559.json` — advanced identical
to the pre-change run on every verdict-level metric (verdict_utility 0.9091,
exact_match 0.9545, grounding 1.0), as required.

**Verdict.** KEPT. The run also confirms the change landed after the final run of
record deliberately: README numbers all trace to `20260830-101148.json`, which this
change cannot and does not alter.

### [13] Final full-set run: the holdout answers
`c369b97` · 2026-08-30 10:11 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** The pre-registered target from the pipeline build (2026-08-29
trajectory header): beat the baseline on verdict_utility AND beat always_abstain
while staying decisive — on the 10 held-out cases never opened during development.

**Change.** No code. Two gates ran before the measurement: the collision sweep
(`eval/results/collision-sweep-2026-08-30.md` — all 32 cases resolve for their
labelled reasons; the two ambiguity cases surface real register namesakes, design
records corrected, resolver untouched) and QREPRO from a fresh clone (101 tests,
§§4–6 executed literally, advanced identical to its paste on every verdict-level
metric). The run itself: flag-less, tagged, clean tree — `git_dirty: false` in the
file, per the standing rule.

**Measurement.** Evidence: `eval/results/20260830-101148.json`, breakdown in
`eval/results/final-breakdown-2026-08-30.md`.

| verdict_utility | all (32) | dev (22) | holdout (10) |
|---|---|---|---|
| advanced | 0.9375 | 0.9091 | **1.0** |
| baseline | 0.5547 | 0.4773 | 0.725 |
| always_abstain | 0.4844 | 0.4886 | 0.475 |

Advanced on the holdout: every metric at its ceiling — verdict_utility 1.0,
confident_wrong_rate 0, check_accuracy 1.0, grounding 1.0, exact_match 1.0,
decisive_rate 1.0. The one imperfection in the full set remains dev case-28, the
deliberately priced B-rating cut. Baseline: 0.5547 full-set — and the holdout was
easier for it at verdict level while harder at check level: verdict_utility 0.725
vs 0.4773 dev, but check_accuracy 0.75 vs 0.8409 and grounding 0.9149 vs 0.9464 —
its extra right answers rest on worse evidence chains. The full-set delta of
+0.3828 is same-run, and the conservative dev-band comparison in entry [1] still
stands.
Advanced cost $0.003142/case (3.6× cheaper than baseline), p50 2.1 s, grounding
1.0 across all 32.

**Verdict.** Target met on the holdout with nothing left on the table: decisive on
every case it should be decisive on, abstaining only where the truth is
unverifiable, zero unverified citations. This is the run of record for every
number in README.md.

### [12] Salary-note advice corrected; live timing recorded; guide refreshed to n=22
`(committed with this entry)` · 2026-08-29 21:05 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** Two user-facing defects from the live Mott MacDonald report, zero
expected dev delta. (1) A figure inside a benefits sentence ("4x basic salary")
tripped the any-digit test from entry [10]'s fix, so `non_annual_unclear` fired where
the truth is `absent` — the check was right that nothing could be established, but
the report told the user to ask the wrong question. New discriminator: a stated rate
carries a currency amount; a bare number in prose does not. (2) Notes carrying their
own terminal punctuation rendered a double full stop.

**Change.** `rules.py::salary_clears_floor` note rule (currency-amount regex);
`report.py` strips trailing punctuation before adding its own. `docs/TIMING.md`
gains measurement 2, stated honestly: baseline 27 s AND correct — an easy case
(refusal in its own section, one register search) — vs advanced 7 s with the refusal
quote grounded across line breaks and the multi-row citation verified live. README
hot take gains the turn: the invariance script catching its own overclaim is the
fifth same-day instance of the pattern and the first where the checking instrument
checked itself — the discipline only works if it is also applied to the thing doing
the checking.

**Measurement.** Evidence: `eval/results/20260829-205818.json` / `205909` / `210352`
(the §4/§5/§6 reproduction refresh, prompts/02 step-6 rule): advanced identical to
`20260829-204901.json` on every metric (0.9091 / 0.0667 / 0.9333 / 0.9545) — the
note-rule change moved nothing on dev, as hypothesised (case-22's wordy note was
already `absent`; case-30's £-rate still fires `non_annual_unclear`). always_abstain
at the computed n=22 floor, 0.4886. REPRODUCTION.md pastes, counts and costs now
predict n=22 outputs.

**Verdict.** KEPT. Both fixes bought correct advice and clean prose, not numbers.

**What this told me to do next.** Saturday is closed. Sunday: collision sweep,
QREPRO, --split all, README fill, note grouping, timing measurement 3, trajectories
audit, video.

### [11] Fixture placement rebuilt under proof; the register check cites deliberately
`e4c1d27` · 2026-08-29 20:49 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** Two defects found by inspecting artifacts rather than metrics. (1) On
a live multi-route entity the register check cited rows[0] — a Creative Worker row —
while the route check cited Skilled Worker; no fixture entity held more than one row,
so the defect survived every case. (2) A placement audit found the source register
opens with ~150 leading-whitespace names that sort first; the fixture insertion had
sorted stripped names, so 26 of 30 fixture rows sat inside that block as its only
spaceless names — enumerable at a glance, while the manifest claimed "name-sorted
positions". Deciding factor for the rebuild (operator): a committed document that is
false as written is a trust defect; a disclosed limitation is honesty.

**Change.** `_decisive_row`: register and route checks cite the same deliberately
chosen row (the Skilled Worker row when held), and multi-route entities have all
routes named in evidence and in the report. All fixture rows repositioned under the
file's own case-insensitive raw-name order; two Quillhaven rows added (case-32, whose
Creative Worker row deliberately precedes its Skilled Worker row); placement pinned by
a test that fails on the pre-repositioning snapshot. **Invariance is a committed
artifact**: `eval/verify_snapshot_invariance.py` proves against the git-history bytes
that matched content is identical for every case and every string the cases exercise;
the one thing repositioning cannot preserve — file-order sequence inside multi-match
lookups — is disclosed per affected case (24, 25) rather than hidden. Manifest and
DATA.md carry the dated history in full. Snapshot filename and date unchanged.

**Denominators, stated explicitly:** dev n=21 → 22, determinable 14 → 15,
always_abstain dev floor → 0.4886.

**Measurement.** Evidence: `eval/results/20260829-204901.json` — advanced 0.9091 /
0.0667 / 0.9333 / exact_match 0.9545, decisive_rate 1.0, grounding 1.0, every figure
as predicted before the run; wrong only on case-28 (the B-rating cut). case-32 cites
the Skilled Worker row with `routes_held: [Creative Worker, Skilled Worker]`. Cases
24 and 25 hold their verdicts across the repositioning — the empirical confirmation
the invariance script's disclosure defers to.

**Verdict.** KEPT. Fourth same-day instance of one pattern — a claim about the
artifact the artifact does not support — and all four passed a green test suite
before being found by looking at the thing itself. That sentence is the hot take.

**What this told me to do next.** Stop. Sunday, in order: collision sweep (32 cases),
QREPRO from a fresh clone, the final --split all run, then README, note grouping,
remaining timing measurements, trajectories audit, video.

### [10] Wrapped quotes canonicalised to source bytes; the fixture that keeps it fixed
`f5e7b67` · 2026-08-29 19:59 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** Real postings hard-wrap; models quote wrapped sentences unwrapped;
the verifier finds no byte-exact substring and downgrades truthful evidence. On live
input the system would systematically lose willingness=offered — a false abstention
on exactly the requisitions the user wants, the project's core failure pointed the
other way. Fix: match under whitespace collapse, map back to the source's true byte
span. Predicted post-fix numbers at dev n=21: verdict_utility 0.9048,
confident_wrong_rate 0.0714, decisive_accuracy 0.9286, exact_match 0.9524.

**Change.** `extract.py::canonicalize_quote` (pure; fabricated text still finds no
span and still fails — verifier semantics and grounding metric unchanged), applied in
`assemble` before the verifier. `case-31-wrapped-quote-offered` added: all twenty
prior dev fixtures kept every quotable sentence on one line — a property real pasted
postings lack — so the blind spot was structural; the case pins it forever. Second
posting from an existing fixture employer; snapshot untouched.

**Denominators changed, stated explicitly (operator condition):** dev n=20 → 21, mix
13/7 → 14/7 determinable/unverifiable, always_abstain dev floor 0.5125 → 0.5. Prior
dev aggregates are not directly comparable to n=21 aggregates; per-case verdicts are.

**Measurement.** Evidence: `eval/results/20260829-195943.json` — every predicted
figure exact: 0.9048 / 0.0714 / 0.9286 / 0.9524, decisive_rate 1.0, grounding 1.0.
case-31: SPONSORABLE, willingness pass/offered, the cited quote is the source's own
bytes with the line break inside it. The original 20 cases: verdicts identical, still
wrong only on case-28 (the B-rating cut). The demo posting that exposed the defect
now reads SPONSORABLE end to end. Baseline note: its grounding dropped to 0.9304 —
its unwrapped quote on case-31 does not ground, which is the defect made visible on
the reference too, honestly.

**Verdict.** KEPT. Third same-day instance of the surface losing what the pipeline
knew, third fix, and this one came from the demo path, not the eval — recorded in
the hot-take candidates: an eval can only measure the failure modes its fixtures
contain, and every fixture set shares properties with its author rather than with
the world.

**What this told me to do next.** Stop for the night. Sunday, in order: collision
sweep (now 31 cases), QREPRO from a fresh clone, the final --split all run, then
README, the 11-entity note grouping, the timing measurement, the video.

### [9] Demo CLI — the product runs outside the harness
`(committed with this entry)` · 2026-08-29 19:30 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** None on eval metrics — stated openly per BP-4, same framing as the
renderer entry. Targets End-to-End Quality and the demo path: until now the product
was exercisable only through the eval harness — an end-to-end gap found while
setting up the human-time measurement. A judge watching the video should see the
tool run on a real posting, not a fixture.

**Change.** `src/advanced/cli.py`: `python -m src.advanced.cli path/to/posting.txt`
— read the pasted posting, one `solve()` call, print the rendered report. No new
dependencies, no pipeline changes. Argument/file errors exit with usage before any
model call (2 tests); documented in REPRODUCTION.md §5 as the demo path.

**Measurement.** No metric moved, none claimed. Verified live on an arbitrary
real-employer posting: the brand resolved against the real register (Sony
Interactive Entertainment → Sony Interactive Entertainment Europe Limited, Skilled
Worker route), salary passed — and the willingness check was DOWNGRADED by the
verifier, correctly by its rules: the posting's sponsorship sentence wraps across a
line break, the model quoted it as a single line, and a line-wrapped quote is not a
byte-verbatim substring.

**Verdict.** KEPT — and the first arbitrary input through the demo path produced a
real finding the twenty dev fixtures could not: real postings hard-wrap, so
byte-verbatim quote matching over-abstains on wrapped sentences. The guarantee fired
in its designed direction (toward UNVERIFIABLE, never confidence), which is the
system working; it is also a false abstention on a posting that plainly offers
sponsorship. Candidate fix for Sunday, operator's call: canonicalise the extracted
quote to the source's true byte span under whitespace normalisation — in code, after
extraction, before the verifier — so evidence gets MORE faithful and no metric or
verifier semantics change.

**What this told me to do next.** Exactly what the operator said this change was
for: exercising the product outside the harness finds what the harness cannot.
Sunday order unchanged: collision sweep, QREPRO, --split all, README.

### [8] Ambiguous resolutions name their candidates — and the register answered back
`acdfdd3` · 2026-08-29 19:12 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** No metric movement — renderer and evidence only. The pipeline knew
which entities matched and that their licences diverge; the report said only "ask
which legal entity". Second same-day instance of a stage knowing more than the report
said.

**Change.** `Ambiguous` carries its candidates' register rows; the register check
cites them as candidate rows (real snapshot content, grounded by construction); an
uncertainty note names each entity with its routes. One new test: an ambiguous
resolution produces a report naming every candidate entity. No new reason values, no
verdict logic.

**Measurement.** Evidence: `eval/results/20260829-191227.json` — verdict_utility
0.9, exact_match 0.95, check_accuracy 0.9875, grounding 1.0: all identical to the
prior run, as required.

**Verdict.** KEPT. And the disclosure taught something the fixtures did not design:
against the real register, "Halcyon Group" is ambiguous across ELEVEN entities — the
two fictional ones plus nine real organisations named Halcyon. The report now shows
the real shape of the problem, including that exactly one candidate (Halcyon
Consulting (UK) Ltd) is Global Business Mobility-only. Readability of an 11-entity
note is a Sunday hardening item (group by route rather than enumerate), flagged to
the operator rather than restyled outside tonight's scope.

**What this told me to do next.** Sunday opens with QREPRO from a fresh clone, then
the final `--split all` run — nothing before those two.

### [7] Code-review fixes: the report tells the whole truth; reasons carry their path
`04f516e` · 2026-08-29 18:59 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** Operator code review found four defects. The serious one: the renderer
rebuilt its unresolved list from check statuses and silently dropped the solver's own
uncertainty disclosures — the B-rating caveat loop 1 added and the salary-as-stated
note never reached the user, so case-28's report claimed "nothing material left
unresolved" while its JSON said otherwise. The others: register reason hardcoded to
legal_name_exact regardless of resolution path; non_annual_unclear never produced;
the same register row printed twice. Expected effect of the reason fixes: exact_match
up, verdict_utility unchanged at 0.9 — any movement there would mean something else
was touched.

**Change.** `assemble` emits structured `uncertainty_notes`; the report renders them
and claims completeness only when nothing remains (pinned by a test that fails on any
report contradicting its result). `resolve_entity` restructured into three phases —
exact over all posting-stated strings, token-subset over all, then the alias pass —
and `Match` carries how it matched (legal_name_exact / trading_name_stated /
alias_lookup), which `_register_check` now emits. `salary_clears_floor` reads the
extraction note: a figure-bearing note means pay was stated but not as guaranteed
annual basic → non_annual_unclear. Shared register rows cite once. verify.py's
docstring no longer promises a register-row gate that could never fail.

**Measurement.** Evidence: `eval/results/20260829-185907.json` — **exact_match 0.75 →
0.95**; verdict_utility exactly 0.9, check_accuracy 0.9875, grounding 1.0, all
unchanged, as required. Cases 01/04 now read `alias_lookup`, 06 `trading_name_stated`,
30 `non_annual_unclear` — each the exact labelled reason. The one remaining
exact_match miss is case-28, whose verdict is the B-rating cut's known price; its
report now displays the B-rating row verbatim AND the rating caveat, so a user
reading it has everything needed to catch what the checks do not.

**Verdict.** KEPT. The acceptance condition held precisely: the target metric moved,
nothing else did.

**What this told me to do next.** Sunday as planned: hardening/QREPRO re-verify,
final `--split all`, README, timing measurement, video.

### [6] Verification report renderer — the user-facing instrument
`ae87f44` · 2026-08-29 09:35 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** None on eval metrics — stated openly per BP-4; the renderer targets
the judged End-to-End Quality criterion directly (docs/PLAN.md §5b, decided
2026-08-28: deterministic pure renderer, no LLM in the render path, because a model
per report reintroduces nondeterminism and the exact register the rubric penalises).

**Change.** `src/advanced/report.py::render_report(result, requisition_text) -> str`.
Fixed-instrument plain English: verdict + determining sentence first; each check with
verbatim evidence (quotes carry character offsets into the source, register rows
reproduced field for field); snapshot date + age warning; an uncertainty section that
names each unresolved check and the concrete action that would resolve it; advisory
close. The six named §5b properties are the tests (`tests/test_report.py`).

**Measurement.** No eval metric moved, none claimed. Render coverage: all 20 dev
cases render without error directly from `eval/results/20260829-090655.json` — the
renderer consumes committed solver outputs, no new model calls.

**Verdict.** KEPT. Built Saturday afternoon instead of Sunday morning (operator
schedule change): 20 judged points should not depend on end-of-competition energy.

**What this told me to do next.** Sunday is now: hardening/QREPRO re-verify, the
final `--split all` run, README fill, the timing measurement, the video.

### [5] Self-consistency voting — REJECTED by its own numbers
`af85076` · 2026-08-29 09:22 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** (Pre-registered, DECISIONS.md 2026-08-28.) 3-sample majority voting
over the frozen baseline at temperature 1.0 costs ~3× per case without beating
deterministic verification on confident_wrong_rate, because sampling one prompt three
times resamples the same blind spots. Run to be rejected by numbers, not argument.

**Change.** `src/experiments/self_consistency.py` — the baseline's exact prompt and
lookup, sampled three times at temperature 1.0 (the one documented C-6 departure;
self-consistency is meaningless at temperature 0). Strict-majority vote; a split
abstains. Registered as an explicit-only eval variant so the rejection is
reproducible: `--variant self_consistency`.

**Measurement.** Evidence: `eval/results/20260829-092222.json`

| Metric | baseline (same run) | self_consistency | advanced |
|---|---|---|---|
| verdict_utility | 0.425 | **0.225** | 0.9 |
| confident_wrong_rate | 0.3571 | **0.4667** | 0.0769 |
| decisive_accuracy | 0.6429 | 0.5333 | 0.9231 |
| check_accuracy | 0.825 | 0.825 | 0.9875 |
| cost_per_case_usd | 0.01097 | **0.03372** | 0.00312 |
| p50_seconds | 9.43 | **29.49** | 2.14 |

**Verdict.** REJECTED — worse than predicted, in the instructive direction. 3.07× the
baseline's cost and 3.1× its latency bought a variant *worse than the baseline it
samples*: temperature diversity added two new wrong verdicts (cases 07, 20) on top of
the seven shared blind spots (04, 06, 11, 26, 28, 29, 30), and check_accuracy did not
move at all — the samples disagree on borderline judgment, not on the things the
prompt cannot see. Voting cannot recover information the lookup never delivered.
Deterministic verification (advanced, 0.9 at $0.0031/case) beats 3× sampling on every
metric at a tenth of the cost.

**What this told me to do next.** The removed-experiment slot is filled with a real
run. Confidence budget goes to code that checks evidence, not to more samples of the
same judgment — which is the submission's thesis, now measured from both directions.

### [4] Stance extractor learns that right-to-work wording settles nothing
`f9f9c31` · 2026-08-29 08:53 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** case-26 flips NOT_SPONSORABLE → UNVERIFIABLE (correct abstention):
verdict_utility +0.10 (a −1.0 becomes +1.0 on one of twenty cases), with case-27 (RTW
wording PLUS an explicit refusal) as the regression sentinel that must stay
NOT_SPONSORABLE.

**Change.** One stance-definition refinement in `extract.py`'s prompt, stated as the
general principle rather than the case: sponsorship itself confers the right to work,
so an RTW requirement alone is "ambiguous", never "refused"; "refused" now requires
an explicit statement that sponsorship is unavailable or sponsorship-needing
candidates excluded. No threshold, route or verdict logic — extraction semantics only
(Condition C respected).

**Measurement.** Evidence: `eval/results/20260829-085330.json`

| Metric | baseline (same run) | advanced | Delta |
|---|---|---|---|
| verdict_utility | 0.225 | **0.9** | +0.675 |
| confident_wrong_rate | 0.4667 | **0.0769** | −0.390 |
| decisive_accuracy | 0.5333 | 0.9231 | +0.390 |
| decisive_rate | 0.8462 | 1.0 | +0.154 |
| check_accuracy | 0.8 | 0.9875 | +0.188 |
| grounding_rate | 0.9691 | 1.0 | +0.031 |
| cost_per_case_usd | 0.01111 | 0.00312 | −72% |

case-26: UNVERIFIABLE with `willingness: indeterminate/boilerplate_ambiguous` — the
exact labelled reason. case-27 sentinel: NOT_SPONSORABLE with `fail/refused` — no
regression. Advanced verdict delta vs its own previous runs: +0.10, exactly the
hypothesis; four prior runs were identical at 0.8, so this is signal, not noise.

**Verdict.** KEPT. 19/20; the single remaining wrong verdict is case-28, the
deliberately cut B-rating sub-check (scope ruling 2026-08-29), whose price is known,
bounded, and stated in that output's own uncertainty statement.

**What this told me to do next.** The dev-split failure surface inside scope is
clear. Next per plan: the verification report renderer (Sunday morning, first), the
removed-experiment run (self-consistency), and the final `--split all` evaluation.

**Conservative delta (appended 2026-08-29, operator ruling).** The frozen baseline
has produced three verdict_utility values across committed runs: 0.225, 0.325, 0.425
— the operative band. Every headline delta is computed against the top of that band,
the worst case for this submission: **+0.475** (0.9 − 0.425), not the +0.675 the
same-run comparison above shows. The advanced side needs no band: five runs at 0.8
(four in-repo, one from a fresh clone) followed by exactly +0.10 after loop 3's
deliberate change — the deterministic stages removed the run-to-run variance the
baseline still has.

### [3] Verifier gates model-sourced quotes ahead of the combinator
`7c85ed0` · 2026-08-29 08:47 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** Zero dev delta — extraction quotes have been verbatim in every
recorded run and grounding already reads 1.0. The layer is structural: after this
change no fabricated quote can reach the output on ANY input, because an unverified
quote downgrades its check to indeterminate and is stripped from evidence before the
combinator runs — a verdict can only move toward UNVERIFIABLE.

**Change.** `assemble()` routes every model-sourced quote through
`verify_and_downgrade` (verify.py) and recomputes the verdict on the verified
outcomes; downgraded checks lose their evidence block and surface as
`evidence_unverified` in the uncertainty statement. One new test (fabricated quote →
UNVERIFIABLE); the four existing assemble tests gained the posting-source argument.

**Measurement.** Evidence: `eval/results/20260829-084751.json` — advanced identical
to the previous three runs on every metric (0.8 / 0.1429 / 1.0 grounding), fourth
consecutive identical result; no downgrades triggered on dev, as hypothesised.

**Verdict.** KEPT. No delta claimed; the change buys a guarantee, not a number.

**What this told me to do next.** Loop 3: the stance-extraction refinement for
case-26 — the last failure the pipeline can address inside its scope.

### [2] Non-A licence rating surfaces in the uncertainty statement
`4e43c41` · 2026-08-29 08:41 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** None on eval metrics — stated openly per BP-4: uncertainty text is
unscored. The change targets output honesty (End-to-End Quality): the B-rating
sub-check is cut by scope ruling, and case-28's output said "nothing material left
unresolved" about a B-rated sponsor that cannot issue a CoS until its action plan
completes.

**Change.** `src/advanced/solve.py::assemble` appends a rating caveat to the
uncertainty statement when the route-cited register row is not "(A rating)"; verdict
unchanged by design. Two new tests (non-A surfaces; A-rated stays quiet).

**Measurement.** Evidence: `eval/results/20260829-084140.json` — regression only:
advanced identical to `20260829-080609.json` on every metric (0.8 / 0.1429 / 1.0 /
0.975 / 1.0); case-28's uncertainty now reads "licence rating not assessed: the
register shows Worker (B rating); …". Baseline landed at 0.425 again, confirming the
widened single-prompt spread noted in REPRODUCTION.md §6.

**Verdict.** KEPT. No delta claimed; none expected. The verdict on case-28 remains
confidently wrong — that is the recorded price of the B-rating cut, now stated in the
output itself rather than hidden.

**What this told me to do next.** Loop 2: wire the verifier (the safety layer earns
its keep outside dev conditions); loop 3: the stance-extraction improvement for
case-26.

### [1] Extract → Resolve → Decide pipeline wired end to end
`f94da46` · 2026-08-29 08:06 UTC · trajectory: `trajectories/2026-08-29-0757-prompt02-pipeline-construction.md`

**Hypothesis.** Splitting the baseline's single judgment call into one extraction call
plus deterministic resolution and rules would eliminate the resolution and threshold
failure classes (docs/PLAN.md §3 failures 2, 3, 5, 8): verdict_utility above both
reference lines, confident_wrong_rate down, grounding at 1.0 — because code reads the
Route column and floor_config, and a model no longer aggregates its own checks.

**Change.** `src/advanced/`: `extract.py` (prompt builder + typed parser; the only
model call), `resolve.py` (normalisation + token-subset matching + alias fixtures;
`GENERIC_TERM_ORG_LIMIT` counts distinct orgs, matched-entity rows uncapped),
`rules.py` (thresholds from floor_config, pure combinator), `solve.py` (wiring +
pure `assemble`). Verifier unit-green, wired in the evening pass. 27 new tests.

**Measurement.** Evidence: `eval/results/20260829-080609.json`

| Metric | baseline (same run) | advanced | Delta |
|---|---|---|---|
| verdict_utility | 0.325 | 0.8 | **+0.475** |
| confident_wrong_rate | 0.4 | 0.1429 | −0.257 |
| decisive_accuracy | 0.6 | 0.8571 | +0.257 |
| decisive_rate | 0.8462 | 1.0 | +0.154 |
| check_accuracy | 0.8125 | 0.975 | +0.163 |
| grounding_rate | 0.951 | 1.0 | +0.049 |
| cost_per_case_usd | 0.01115 | 0.00298 | −73% |
| p50_seconds | 10.08 | 2.23 | −78% |

Against the frozen reference run (`20260829-002858.json`, baseline 0.225) the delta is
+0.575; against the same-run baseline above, +0.475. The noise floor is stdev 0.049 on
verdict_utility (`20260829-002003.json`), so the conservative delta is ~10σ. The
same-run baseline's 0.325 sits at the top of its measured range (0.225–0.325) —
consistent with noise, stated for honesty.

**Verdict.** KEPT. The pre-registered target (DECISIONS.md 2026-08-29) is met: beats
the baseline on verdict_utility (0.8 > 0.325) AND always_abstain on decisive_rate
(1.0 > 0) while decisive_accuracy rose (0.857 vs 0.6) — the gain is not abstention
drift; the advanced variant answers every determinable case and abstains on 6 of 7
truly unverifiable ones.

**Band note (appended 2026-08-29).** The deltas above were computed before the
operative baseline band was established; the standing conservative figure is defined
in entry [4]: computed against the band top (0.425), not any single run's pairing.
Every README delta comes from the band.

**What this told me to do next.** 18/20; the two remaining wrong verdicts are exactly
diagnosable, which is the pipeline's point. case-26: the extraction model classified
right-to-work boilerplate as "refused" — a stance-extraction error, the evening's
first measured improvement candidate. case-28: all four checks pass because nothing
reads the licence rating — the deliberately cut B-rating sub-check's price, one
confident-wrong; per the cut ruling the rating must at least surface in the
uncertainty statement, which it currently does not. Evening order: wire the verifier,
then one measured improvement per prompts/02 loop.

### [0] Baseline frozen
`cde01b2` · 2026-08-29 00:28 UTC · trajectory: `trajectories/2026-08-28-1833-prompt01-cases-and-baseline.md`

**Change.** Deliberately simple reference implementation in `src/baseline/solve.py`: one
pinned-model call (`claude-sonnet-4-6`, temperature 0.0) carrying the pasted requisition
plus a naive register lookup (most-specific name candidate wins; generic words skipped;
blindness to trading names, routes and ratings preserved by design). The prompt is basic
instructions only — four plain-language questions, the floor figures as data, the output
contract; no reason vocabulary, no threshold-combination rule, no pay-composition rule.
It is a faithful reproduction of the manual process in use today (README, "Baseline
solution"). **Frozen from commit `cde01b2` onward per CN-3 — never edited again. Every
later delta is measured against this exact file.**

Two superseded runs are part of the record, not the baseline: `eval/results/20260828-224144.json`
(a lookup defect delivered unrelated register rows on 5 of 20 dev cases — numbers
depressed, unfair as a reference; DECISIONS.md 2026-08-29) and `eval/results/20260829-002446.json`
(same numbers, dirty-tree flag; superseded by the clean rerun below).

**Measurement.** Evidence: `eval/results/20260829-002858.json` (reference table, clean
tree, seed 42, dev split). Noise floor: `eval/results/20260829-002003.json` (`--repeats 5`).

| Metric | baseline | always_abstain | advanced |
|---|---|---|---|
| verdict_utility | 0.225 | 0.5125 | — (stub) |
| confident_wrong_rate | 0.4667 | 0 | — |
| decisive_accuracy | 0.5333 | 0 | — |
| decisive_rate | 0.8462 | 0 | — |
| check_accuracy | 0.8 | 0 | — |
| grounding_rate | 0.99 | 0 | — |
| cost_per_case_usd | 0.01123 | 0 | — |
| error_rate | 0 | 0 | 1.0 (empty slot by design) |
| p50_seconds | 9.814 | ~0 | — |

Run-to-run noise (5 repeats, same seed): verdict_utility mean 0.265, stdev 0.04899
(range 0.225–0.325); confident_wrong_rate mean 0.44, stdev 0.03266; check_accuracy mean
0.8075, stdev 0.02031; grounding_rate mean 0.9644, stdev 0.007984; decisive_rate stdev 0.
**A verdict_utility delta smaller than ~0.1 (2σ) is noise, not a result.**

**What this told me to do next.** The baseline is decisive (84.6% of determinable cases
answered), well-grounded (0.99), and wrong on 46.7% of its definitive verdicts — its
utility sits 0.29 *below* trivial abstention. The failure is judgment, not retrieval:
route conflation (case-07 reads "Worker (A rating)" as route coverage while the Route
column says GBM), threshold aggregation (case-11's own failing salary check waved
through to SPONSORABLE), stance misreads (cases 20, 26), and name resolution (01, 04,
06 — case-04 is the only SPONSORABLE lost to it). Saturday builds exactly those stages:
extract → resolve (alias layer in scope) → rules engine reading `floor_config` — no
threshold or route logic in any prompt — with a measured dev-split run by midday; the
verifier in the evening; the report renderer Sunday morning. B-rating sub-check cut to
the uncertainty statement. Success target pre-registered in DECISIONS.md 2026-08-29:
beat the baseline on verdict_utility AND always_abstain on decisive_rate while holding
decisive_accuracy high.

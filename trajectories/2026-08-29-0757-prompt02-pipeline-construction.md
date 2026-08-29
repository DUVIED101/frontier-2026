# Trajectory — prompt02-pipeline-construction

| Field | Value |
|---|---|
| Date (UTC) | 2026-08-29, session start 07:57 |
| Agent | Claude Code (CLI), operator-gated per prompts/02 discipline |
| Model | claude-fable-5 (session agent); claude-sonnet-4-6 pinned for both solver variants |
| Tools granted | file edit/read, bash, git; API access via ANTHROPIC_API_KEY (workspace-scoped) |
| Instruction file | `CLAUDE.md` + Saturday scope ruling (2026-08-28 session close) + this morning's checkpoint |
| Task | Build the advanced pipeline: extract → resolve → rules → wire → measured dev run |
| Expected metric impact | verdict_utility ↑ (pre-registered target: beat baseline 0.225 AND always_abstain decisive_rate 0 while holding decisive_accuracy high); confident_wrong_rate ↓ from 0.4667 |
| Commit at start | `95345d5` |

Morning exit condition (operator, verbatim in substance): a MEASURED dev run, not a
finished pipeline — every stage minimally working and measured beats two stages
polished and unmeasured. Report the first advanced-vs-baseline table however weak.
Build order: extract → resolve → rules → wire end to end → run. prompts/02 governs
from the first improvement AFTER the pipeline runs; this build is construction.

---

## Session

### Step 0 — Two pre-resolver items from the morning checkpoint

> **HUMAN: redirected** — before the resolver: (1) the baseline's MAX_REGISTER_ROWS
> doubles as display cap and generic-word threshold — frozen, left alone; the advanced
> resolver must separate the concerns, named distinctly, boundary tested. A real
> company name can legitimately match more rows than an excerpt should carry;
> conflating the two discards genuine matches. (2) always_abstain's grounding_rate 0
> means "no citations issued", not "cites badly" — noted in README now so the Sunday
> table does not read as a false comparison.

**Agent action + tool responses, in order**

```
resolver design         -> the resolver counts distinct ORGANISATIONS to detect
                           generic words (GENERIC_TERM_ORG_LIMIT); a matched entity's
                           own rows are returned UNCAPPED — display concerns belong to
                           the renderer, not resolution. Two boundary tests written
                           red first: a 25-row single org must Match with all rows; a
                           string matching >LIMIT distinct orgs is generic -> skipped.
README                  -> grounding_rate footnote added next to the results table.
```

### Step 1 — Construction: all four stages green in one TDD pass

**Agent action + tool responses, in order**

```
TDD                     -> 5 new red tests first (2 resolver-boundary, 3 extraction
                           parse) on top of the 20 scaffold reds.
rules.py                -> pure functions green: salary reads both thresholds from
                           floor_config (binding = max), route reads the Route column
                           (SW present / GBM-only / other), willingness maps stance,
                           combinator any-fail->NS / all-four-pass->S / else U.
resolve.py              -> normalised-name index + token-subset matching + alias pass.
                           GENERIC_TERM_ORG_LIMIT counts distinct ORGS (generic-word
                           guard); matched entity rows returned UNCAPPED — the two
                           concerns the baseline conflates, separated per checkpoint.
verify.py               -> mechanical quote gate implemented (unit-green); wired into
                           the pipeline in the evening pass, per scope.
extract.py              -> prompt builder + typed parser (C-5 errors); the API call
                           lives in solve.py so I/O stays at the edge (C-4). One
                           scaffold refinement recorded: extract_claims() dropped in
                           favour of build_extraction_prompt()+parse_claims() —
                           mirrors the frozen baseline's structure (C-2).
solve.py                -> wired: extract (1 model call) -> resolve -> rules ->
                           assemble (pure, 2 policy tests: register presence does not
                           imply sponsorability; silence blocks S without producing
                           NS). Same pinned model/temperature as baseline.
gates                   -> 65/65 green; mypy --strict clean (10 files); ruff clean.
resolver smoke (real)   -> 143,018 rows, 0.3s load, <0.5s/query: Ottervale -> Match
                           Bryelock Systems Ltd (alias, the case-01 two-hop);
                           Loopwork -> Ashcombe Digital Ltd; "Halcyon Group" ->
                           Ambiguous over both entities; "Veltrix Software Limited"
                           -> Veltrix Software Ltd; unlisted -> NoMatch.
```

**What this changed about the plan**

Nothing — the morning order held. Committing everything BEFORE the eval launches
(the dirty-tree lesson from last night, applied).

### Step 2 — First measured run: 18/20, both reference lines beaten, target met

**Agent action + tool responses, in order**

```
run (tag first-pipeline)-> eval/results/20260829-080609.{json,md}, clean tree at
                           f94da46, 40 model calls, 0 errors. advanced 0.8 utility /
                           0.143 confident_wrong / decisive_rate 1.0 / grounding 1.0
                           / $0.003 per case / p50 2.2s — beats baseline (0.325) and
                           always_abstain (0.5125); conservative delta +0.475 ≈ 10σ
                           against the recorded noise floor. Pre-registered target
                           met with decisive_accuracy UP (0.857 vs 0.6): not
                           abstention drift.
failure dig             -> the two wrong verdicts, from the per-check record:
                           case-26: extraction classified RTW boilerplate as
                           "refused" (willingness fail -> NS). The trap survived the
                           stance-definition prompt; evening improvement candidate.
                           case-28: all four checks pass — nothing reads the licence
                           rating (B-rating check deliberately cut). The cut's price
                           is this one confident-wrong; worse, the uncertainty
                           statement says "nothing material left unresolved", which
                           overstates confidence for a B-rated sponsor. The cut
                           ruling requires the rating to surface in uncertainty —
                           evening item, verdict unchanged.
CHANGELOG [1]           -> written citing 20260829-080609.json; KEPT.
```

### Step 4 — Evening loop 1: rating caveat in uncertainty (no-metric change, measured anyway)

```
TDD                     -> red test: B-rated SW row must surface in uncertainty
                           without changing the verdict; A-rated stays quiet.
implement               -> assemble() reads the route-cited row's type_rating; non-A
                           appends the caveat. 67/67 green, mypy clean.
measured run            -> 20260829-084140.json (clean tree, 4e43c41): advanced
                           IDENTICAL to 080609 on every metric — regression none;
                           case-28 uncertainty now carries "Worker (B rating)"
                           caveat. Baseline 0.425 again (single-prompt spread now
                           0.225-0.425 across committed runs). CHANGELOG [2], BP-4
                           no-delta stated.
```

### Step 5 — QREPRO passes from a fresh clone; evening loop 2 wired and measured

```
QREPRO (literal)        -> fresh clone at /tmp/frontier-qrepro; executed every
                           REPRODUCTION.md command in order as written. §1 venv+pip
                           clean; §2 key config as documented; §7 gates 65/65 green,
                           mypy clean, ruff clean, no context assumed. §4 baseline
                           0.425 (within the documented 0.225-0.425 spread); §5
                           advanced 0.8 IDENTICAL to the pasted expected output;
                           §6 full table 0.425/0.5125/0.8. The two dirty-tree
                           warnings appeared exactly where §6 documents them. Only
                           non-executable step: the <REPO_URL> placeholder, filled at
                           submission. Docker Option B verified separately (build +
                           65/65 in container + harness run).
loop 2 (verifier)       -> TDD: fabricated-quote red test; assemble() now verifies
                           every model-sourced quote before combine, strips evidence
                           on downgrade. 68/68 green. Measured run
                           20260829-084751.json (clean, 7c85ed0): advanced identical
                           FOURTH consecutive run (0.8 / 0.1429 / 1.0); zero
                           downgrades on dev as hypothesised. CHANGELOG [3]: the
                           change buys a guarantee, not a number.
```

### Step 6 — Evening loop 3: stance refinement lands exactly on hypothesis

```
change                  -> one stance-definition refinement in the extraction prompt,
                           stated as the general principle (sponsorship itself
                           confers the right to work; RTW wording alone is ambiguous,
                           never refused; refused requires an explicit exclusion).
                           No threshold/route/verdict logic (Condition C).
measured run            -> 20260829-085330.json (clean, f9f9c31): advanced 0.9 /
                           cwr 0.0769 / decisive_accuracy 0.9231 / check_accuracy
                           0.9875 / exact_match 0.75. case-26 -> UNVERIFIABLE with
                           the exact labelled reason (boilerplate_ambiguous);
                           case-27 sentinel held (fail/refused). +0.10 on advanced
                           after four identical 0.8 runs: signal, not noise.
                           19/20 — the single wrong verdict is case-28, the
                           deliberately cut B-rating check, priced and disclosed in
                           its own output. Baseline same-run 0.225 (low end of its
                           spread); same-run delta +0.675.
```

### Step 7 — Operator corrections before the removed-experiment run

> **HUMAN: redirected** — four rulings. (1) Conservative delta: every headline claim
> computes against the WORST committed baseline figure (band 0.225–0.425, three
> observed values) — +0.475, not the same-run +0.675; appended to CHANGELOG [4]
> without editing earlier entries, and written into the prompts/02 loop as a standing
> rule. (2) The Docker finding is submission material, not just a fix: an unexercised
> "recommended" path that would have baked the API key into an image layer, FOUND BY
> QREPRO — not routine maintenance. It instantiates the project's own thesis: an
> untested path that looks correct is not evidence; verification separates the two.
> Seeded into README (reproduction section + hot-take candidates). (3) Loop 2 stays
> reported exactly as measured: zero dev delta, kept for the guarantee — a component
> described as an improvement it did not deliver is what the evidence chain exists to
> prevent. Seeded into README. (4) REPRODUCTION.md went stale the moment loop 3
> changed a number a judge would see (§5 pastes 0.8, suite is 68 not 65, variance
> band now has three observed values). Fixed; §§4–6 re-verification added to the
> prompts/02 loop as step 6 so it cannot drift again. Then the removed-experiment
> run, then stop — Sunday opens with the renderer.

```
CHANGELOG [4]           -> conservative-delta paragraph appended (band, worst-case
                           +0.475, advanced needs no band: five identical runs).
prompts/02              -> loop gains: conservative-delta rule (step 3) and
                           REPRODUCTION §§4-6 re-verification (step 6).
README seeds            -> determinism-as-measured-property; verifier honest framing;
                           Docker-found-by-QREPRO in reproduction section; two
                           hot-take candidates recorded as they happened.
REPRODUCTION            -> §6 variance rewritten (three observed values, band top is
                           0.425, advanced five identical runs incl. fresh clone);
                           §7 count 68. §5/§6 pastes refresh from fresh runs next.
```

### Step 8 — Removed experiment rejected; renderer built a day early

> **HUMAN: redirected** — schedule change: more operator time today than planned.
> After the removed-experiment entry, continue into the verification report renderer
> this afternoon rather than Sunday morning: 20 judged points against one changelog
> entry, and Sunday is already full. Scope stays PLAN §5b exactly.

```
experiment              -> 20260829-092222.json: self_consistency 0.225 utility at
                           $0.0337/case and p50 29.5s — WORSE than the same-run
                           baseline (0.425) it samples; two NEW wrong verdicts from
                           temperature diversity on top of the seven shared blind
                           spots; check_accuracy unchanged. Voting cannot recover
                           information the lookup never delivered. REJECTED by its
                           own numbers; CHANGELOG [5]; DECISIONS evidence completed.
renderer (TDD)          -> six §5b-named tests red first; render_report implemented
                           as a pure function: verdict+why lead, quote evidence with
                           character offsets verified as spans, register rows field
                           for field, snapshot age warning, per-unresolved-check
                           actions ("what the user would have to do"), advisory
                           close. 78/78 green; mypy clean (13 files).
render coverage         -> all 20 dev cases render without error straight from the
                           committed results file (no model calls). case-22 (truth
                           UNVERIFIABLE) shown to operator: three PASSes with real
                           evidence, salary UNRESOLVED with the concrete ask.
                           CHANGELOG [6] (BP-4: no metric, E2E Quality target).
```

### Step 9 — Operator code review: four defects, one serious; all fixed and measured

> **HUMAN: redirected** — review verdict: architecture right (pure combinator,
> thresholds only from floor_config, extraction asks what the posting says); four
> defects. (1) SERIOUS: the renderer discarded result uncertainty entirely — the
> B-rating caveat and salary note existed in JSON and never reached the user; the
> report claimed the exact completeness sentence loop 1 was built to prevent. A
> regression at the layer a judge reads. (2) register reason hardcoded to
> legal_name_exact. (3) non_annual_unclear never produced. (4) register row printed
> twice. Plus: delete verify.py's promise of register-row gates rather than build a
> check that cannot fail; append a band note to CHANGELOG [1] pointing at [4]'s
> conservative recomputation. Fix 1 first; 2+3 together with one re-run — exact_match
> should move and nothing else.

```
fix 1+4 (renderer)      -> red tests first: report-contradicts-result completeness
                           test; shared-row-once test. assemble emits structured
                           uncertainty_notes (salary note + rating caveat); report
                           renders them, claims completeness only when nothing
                           remains; shared row cited once, route references it.
fix 2 (via-path)        -> resolver restructured into three phases (exact over all
                           stated strings, subset over all, THEN aliases — the
                           posting's own words outrank fixtures); Match.via carries
                           legal_name_exact / trading_name_stated / alias_lookup.
                           Boundary pins updated to assert via explicitly; new pin:
                           stated legal name wins BEFORE any alias. Extraction
                           prompt: primary name first (was "most specific first" —
                           which would have mislabelled 06 as legal_name_exact).
fix 3 (salary note)     -> salary_clears_floor(note=...): figure-bearing note ->
                           non_annual_unclear; wordy note stays absent. 2 red tests.
fix 5                   -> band note appended to CHANGELOG [1], no rewrite.
measured run            -> 20260829-185907.json (clean, 04f516e): exact_match 0.75
                           -> 0.95; verdict_utility EXACTLY 0.9, check_accuracy and
                           grounding unchanged — the acceptance condition ("if
                           verdict_utility moves, something else was touched") held.
                           01/04 alias_lookup, 06 trading_name_stated, 30
                           non_annual_unclear — exact labelled reasons. Remaining
                           exact_match miss: case-28, the cut's known price; its
                           report now shows the B-rating row verbatim AND the caveat.
                           83/83 tests, mypy clean. CHANGELOG [7].
```

### Step 10 — Ambiguity disclosure; a pattern named; the register answers back

> **HUMAN: redirected** — do it tonight; the reading of the gap is right. And the
> finding outranks the fix: TWICE in one day the pipeline knew more than the report
> said — once is an oversight, twice in the same layer is a pattern. Principle,
> recorded as ordered: **the evidence a stage produces must reach the user unless
> there is a reason it should not.** These systems leak at the seam between what a
> stage computes and what the surface repeats; every reduction (a status summarising
> rows, a sentence summarising a struct) is a place where knowledge silently drops.
> Goes into README's engineering section tomorrow as one line.

```
TDD                     -> red test: an ambiguous resolution produces a report naming
                           every candidate entity.
implement               -> Ambiguous carries its candidates' rows (resolver builds
                           them at return); register check cites candidate rows;
                           assemble writes an uncertainty note naming each entity
                           with its routes. 84/84 green; mypy clean.
regression run          -> 20260829-191227.json (clean, acdfdd3): verdict_utility
                           0.9, exact_match 0.95, check_accuracy 0.9875, grounding
                           1.0 — identical to the digit, acceptance condition held.
the register answers    -> the fixtures designed a 2-entity ambiguity; the REAL
                           register makes "Halcyon Group" ambiguous across 11
                           entities (2 fictional + 9 real Halcyons), exactly one of
                           them GBM-only. The disclosure is honest about the real
                           shape of the problem; the 11-entity note's readability
                           (group by route rather than enumerate) is flagged for
                           Sunday hardening, not restyled outside tonight's scope.
```

---

## Close (TR-5)

**Shipped.** The advanced pipeline end to end (extract → resolve → rules → verifier)
with the alias layer; the deterministic verification-report renderer (§5b, six named
properties); the self-consistency experiment module (kept runnable); REPRODUCTION.md
filled with literal commands and recorded outputs, verified by a fresh-clone QREPRO;
the Docker path fixed (COPY-context bug, .env-in-layer hazard) and exercised
in-container; CHANGELOG [1]–[8]; the operator code-review fixes (uncertainty carried
to the report, resolution-path reasons, non_annual_unclear, row dedup); ambiguity
disclosure. 84 tests, mypy --strict clean, every run from a clean tree.

**Metric moved.** verdict_utility: baseline band 0.225–0.425 → advanced 0.9
(conservative delta +0.475 against the band top; three identical 0.9 runs).
confident_wrong_rate 0.4667 → 0.0769. decisive_rate 1.0 with decisive_accuracy
0.9231 — the pre-registered target met without abstention drift. exact_match 0 →
0.95. grounding_rate 1.0. cost_per_case −72%, p50 −78%. Evidence:
eval/results/20260829-191227.json (current), 20260829-092222.json (rejected
experiment), and the day's chain of tagged runs.

**Discarded.** Self-consistency voting — rejected by its own numbers (worse than the
baseline it samples at 3.07× the cost; two NEW wrong verdicts from temperature
diversity). The "most specific first" extraction ordering (would have mislabelled
trading-name cases). verify.py's promised register-row gate (a check that cannot
fail). The renderer's independent uncertainty derivation (the serious review defect:
it dropped what the pipeline knew).

**Next.** Sunday, in order and nothing before them: QREPRO from a fresh clone, the
final --split all run. Then README (including the leak-pattern line in engineering
and the case-01 limitation), the 11-entity note readability item, the
time-to-a-trustworthy-answer measurement, trajectories audit, the video, submit.

---

### Post-close checkpoint (received 2026-08-29 evening, scheduled for Sunday morning)

> **HUMAN: redirected** — front of the hardening list, FIRST thing Sunday, before
> QREPRO: a collision sweep. "Halcyon Group" matching eleven entities (nine real)
> means the fixture design assumed two candidates and the real register supplied nine
> more; the collision tests checked exact matches of fictional names, never partial
> or token-level collisions between a case's employer strings and real rows.
> Case-24's verdict is right partly by accident. Run every case's employer strings
> through the resolver against the committed snapshot; report per case how many
> entities match and by which path; any case whose resolution differs from its design
> assumption is a finding — the label may still be right, but we must know whether it
> is right FOR THE LABELLED REASON (a check_accuracy and exact_match question, not a
> verdict one). Nothing found -> ten minutes spent and the README gains a sentence
> (fixtures verified against real collision behaviour, not just exact-name absence).
> Something found -> better Sunday morning than in a judge's re-run. The 11-entity
> readability fix (group by route) comes AFTER the sweep — the presentation fix
> assumes the resolution is correct. Then QREPRO, then --split all, then README.
>
> Sweep design note, recorded tonight: the machine-checkable design assumption is
> expected.checks.register (status + reason path); holdout cases are swept
> mechanically with only counts, paths and OK/DIFFERS booleans surfaced — payloads,
> labels and strings stay inside the script (holdout discipline). The
> asserted-absent class is the sharpest risk: absence was verified under
> normalisation equality before the token-subset phase existed.

### Post-close checkpoint 2 — Demo CLI ordered; its first run finds what fixtures cannot

> **HUMAN: redirected** — request: a minimal CLI (`python -m src.advanced.cli
> posting.txt`) reading a pasted posting, running solve(), printing the report.
> Reason: the product was exercisable only through the eval harness — an end-to-end
> gap found while setting up the human-time measurement by hand; a judge watching the
> video should see the tool on a real posting, not a fixture. What it changed: the
> demo path exists, is documented in REPRODUCTION §5, and is the video walkthrough.

```
TDD                     -> 2 red tests (usage / missing file exit before any model
                           call); cli.py implemented; 86/86 green, mypy clean.
live verification       -> operator's sony.txt is an unsaved buffer (not on disk);
                           verified instead on an arbitrary real-employer posting in
                           /tmp. End to end: "Sony Interactive Entertainment"
                           resolved against the REAL register to Sony Interactive
                           Entertainment Europe Limited (Skilled Worker), salary
                           passed — and willingness was DOWNGRADED by the verifier:
                           the sponsorship sentence wraps across a line break, the
                           model quoted it unwrapped, not byte-verbatim -> honest
                           UNVERIFIABLE.
FINDING                 -> the guarantee fired in its designed direction on the FIRST
                           arbitrary input — and it is also a false abstention: real
                           postings hard-wrap; none of the twenty dev fixtures wrap a
                           quote across a line. Candidate Sunday fix (operator's
                           call): canonicalise extracted quotes to the source's true
                           byte span under whitespace normalisation, in code, after
                           extraction — evidence becomes MORE faithful; no metric or
                           verifier semantics change. The demo path justified itself
                           on its first run: exercising the product outside the
                           harness finds what the harness cannot.
```

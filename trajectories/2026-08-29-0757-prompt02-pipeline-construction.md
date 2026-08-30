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

### Post-close checkpoint 3 — Wrapped-quote defect fixed tonight by order; predictions exact

> **HUMAN: redirected** — fix tonight, not Sunday: "a false abstention on a posting
> that plainly offers sponsorship is the failure this project exists to avoid,
> pointed the other way." Conditions: match under whitespace normalisation, map back
> to the source's true byte span (verifier semantics and grounding metric unchanged);
> add one dev fixture whose sponsorship quote wraps — the fix without the fixture
> leaves the blind spot; state denominator changes explicitly and re-run; the
> three-instances-in-one-day pattern goes in the hot take.

```
TDD                     -> 4 red tests (canonicalize x3, assemble repair x1);
                           canonicalize_quote implemented (regex over escaped tokens
                           joined by \s+; fabricated text finds no span and still
                           fails). case-31-wrapped-quote-offered authored: second
                           Thornber posting, sponsorship sentence wraps mid-phrase
                           ("Skilled\nWorker"), labelled anchor is source bytes.
                           90/90 green; mypy clean.
live proof              -> the demo posting that exposed the defect now reads
                           SPONSORABLE; the report renders the quote with the line
                           break inside it and valid offsets.
measured run (n=21)     -> 20260829-195943.json (clean, f5e7b67): every predicted
                           figure exact — 0.9048 / 0.0714 / 0.9286 / 0.9524,
                           decisive_rate 1.0, grounding 1.0. Original 20 verdicts
                           identical; wrong only on case-28 (the cut). Denominators
                           stated: n=21, abstain floor 0.5. Baseline grounding fell
                           to 0.9304 — its unwrapped quote on case-31 does not
                           ground: the defect made visible on the reference too.
hot take                -> third bullet recorded: three same-day instances of the
                           surface losing what the pipeline knew, all found by
                           reading output rather than metrics; an eval measures only
                           the failure modes its fixtures contain, and fixture sets
                           share properties with their author, not the world.
STOPPED                 -> Sunday order unchanged: collision sweep (31 cases),
                           QREPRO, --split all, then README / note grouping /
                           timing / video.
```

### Post-close checkpoint 4 — Live timing result; a citation defect visible in it

> **HUMAN: redirected** — timing measured on a live Sony Music posting: baseline 130s
> (two questions plus manual register verification), advanced 7s, same verdict, and
> advanced reached it for better reasons — the baseline substituted a market estimate
> ("£70-90k for a London SWE role") for a salary the posting does not state, while
> advanced returned indeterminate and quoted what the posting actually says. That is
> §3 failure mode 1 (world-knowledge substitution) caught on live input — the failure
> the synthetic fixtures structurally cannot elicit (DECISIONS 2026-08-29), observed
> in the wild on the first real employer.
>
> Defect visible in that output, ordered fixed tonight alongside the wrapped-quote
> work (both are evidence-selection bugs): Sony Music holds four register rows across
> four routes and _register_check cites rows[0] — the report said "on the register —
> Temporary Worker (A rating) · Creative Worker" while the route check cited the
> Skilled Worker row. A user is misled about what was established. The register check
> must cite deliberately (the row the verdict rests on) and the multi-licence fact
> must reach the user. A dev fixture with a multi-row entity is required — same
> reasoning as case-31: the defect survived because no fixture had this shape.

### Post-close checkpoint 5 — Sourcing finding: the affirmative-sponsorship posting does not exist in the wild

> **HUMAN: redirected** — for the evidence file and the README, as a finding: no live
> posting could be sourced that affirmatively offers sponsorship for a specific role.
> That matches the domain — sponsorship is rarely stated; silence is the common case,
> not the edge case. It is the empirical justification for the C3 silence policy:
> silence blocks SPONSORABLE without producing NOT_SPONSORABLE, so the system's most
> frequent honest output is UNVERIFIABLE with a named question to ask. A judge who
> assumes silence means refusal reaches the opposite policy and discards viable
> roles. The timing sample is three requisitions across the classes that could
> actually be sourced — three requisitions illustrate; the full case eval carries the
> statistical weight. Also ordered for README: present the case-31 denominator shift
> plainly (abstain floor 0.5125 -> 0.5; baseline grounding 0.9304 because its
> unwrapped quote does not ground either) as the fixture set becoming slightly more
> like the world and slightly less like its author — per-case verdicts are what carry
> across the change.

### Post-close checkpoint 6 — Snapshot placement audit; rebuild ruled

> **HUMAN: approved (rebuild)** — while locating the Quillhaven insertion point, a
> position audit found the real file opens with a leading-space-name block (lines
> 1-150, a genuine gov.uk artifact) and 26 of 30 fixture rows sit inside it as its
> ONLY spaceless rows — enumerable at a glance, several pairs mutually unordered.
> Solvers never see file position (provable), but the manifest and DATA.md claim
> "inserted at name-sorted positions", which the artifact does not do. Operator's
> deciding factor: consequence 3, not 2 — "a committed document that is false as
> written is a trust defect... Do not ship docs you would have to caveat verbally."
> Conditions: (1) the invariance proof is a COMMITTED, runnable script comparing both
> snapshots per case, referenced from DATA.md — without it every results file [1]-[10]
> silently references bytes that no longer exist in the repo; (2) DATA.md and the
> manifest carry the dated history in full — the paragraph is worth more than clean
> provenance, it shows the integrity check running against our own work; (3) the
> hardened test fails on the current snapshot before passing on the new one (case-31
> principle); (4) filename and snapshot date unchanged — content moved, the source
> and its date did not. Pattern upgraded to four instances of one class: a claim
> about the artifact the artifact does not support (B-rating, ambiguity candidates,
> wrapped quote, sorted-positions note), all found by inspecting the thing itself,
> ALL FOUR PASSING A GREEN TEST SUITE — that is the hot take.

### Post-close checkpoint 6 (execution) and second close — rebuild under proof; stopped

```
placement test          -> RED on old snapshot (fixture rows sort after their
                           successors inside the leading-space block) -> rebuild ->
                           GREEN. Condition 3 satisfied in order.
rebuild                 -> all fixture rows repositioned under the file's own
                           case-insensitive raw-name order; Quillhaven x2 inserted at
                           rows 100905-100906 (Creative Worker first, the defect
                           shape); 143,020 data rows; real rows byte-identical
                           (multiset-verified); CRLF/no-BOM/trailing-newline
                           preserved; filename and date unchanged (condition 4).
invariance proof        -> eval/verify_snapshot_invariance.py committed (condition
                           1). First run CAUGHT its own overclaim: strict byte
                           identity is impossible — multi-match lookups return rows
                           in file order, and repositioning reorders them (case-25
                           baseline excerpt, cases 24/25 ambiguity listings). The
                           claim was weakened honestly to content-identity with
                           per-case reorder disclosure, not hidden. Exit 0: content
                           identical everywhere.
docs                    -> manifest note + DATA.md placement-history paragraph in
                           full (condition 2); README denominator note, hot take v2
                           (four instances, all passed a green suite), limitation
                           paragraph closed with the live observation; TIMING.md
                           created with measurement 1 and the sourcing finding.
run (n=22)              -> 20260829-204901.json (clean, e4c1d27): advanced 0.9091 /
                           0.0667 / 0.9333 / em 0.9545, wrong only on 28; case-32
                           cites the SW row with both routes held; cases 24/25
                           verdicts hold across the repositioning. CHANGELOG [11].
STOPPED                 -> Sunday: collision sweep (32 cases), QREPRO, --split all,
                           README, note grouping, timing 2-3, trajectories audit,
                           video.
```

### Post-close checkpoint 7 — Timing complete on live input; two note defects; the turn

> **HUMAN: redirected** — timing measurement 2 (Mott MacDonald, live): baseline 27s
> AND CORRECT — an easy case, and the evidence file must say so rather than flatter
> the comparison (refusal in its own section, one register search). Advanced 7s,
> NOT_SPONSORABLE, quote grounded across line breaks; the multi-row citation fix
> verified on live input (three routes named, decisive row stated). Two user-facing
> defects in that report, fixed with the timing commit: (1) double full stop — notes
> carry terminal punctuation and the template added another; (2) non_annual_unclear
> misfired on "4x basic salary" inside a benefits sentence — the any-digit test from
> the earlier fix read it as a stated rate and the report told the user to ask the
> wrong question. New rule: a stated rate carries a currency amount; a bare number in
> prose does not. And the naming of the pattern's fifth instance: the invariance
> script catching its own overclaim — the first where the checking instrument checked
> itself. Ordered into the hot take as the TURN, not a fifth bullet: the discipline
> only works if it is also applied to the thing doing the checking.

```
TDD                     -> 2 red tests (benefits-figure note -> absent; note renders
                           one full stop); currency rule in salary_clears_floor;
                           punctuation strip in the report renderer. 94/94 green;
                           mypy clean. Dev-set impact expected nil (case-22 wordy
                           note -> absent unchanged; case-30 £-rate -> non_annual
                           unchanged); confirmed by the refresh runs below.
```

---

## Final close (TR-5, superseding the earlier close — the session continued by order)

**Shipped since the first close.** Demo CLI (the product outside the harness);
wrapped-quote canonicalisation + case-31; multi-row deliberate citation + case-32;
fixture placement rebuilt under committed proof (eval/verify_snapshot_invariance.py)
with the full dated history in DATA.md; salary-note advice corrected (currency rule)
+ punctuation fix; docs/TIMING.md with two live measurements and the sourcing
finding; REPRODUCTION refreshed to n=22; CHANGELOG [9]-[12]. 94 tests, mypy --strict
clean, tree clean at every run.

**Metric state at close.** Dev n=22: advanced 0.9091 / cwr 0.0667 / decisive 1.0 &
0.9333 / check 0.9886 / grounding 1.0 / exact_match 0.9545 / $0.0032/case / p50
2.1s; wrong only on case-28 (the priced B-rating cut). References: baseline 0.2955
(this session), always_abstain 0.4886. Advanced identical across all three n=22
runs. Evidence: 20260829-204901 / 205818 / 205909 / 210352.

**Discarded since the first close.** The any-digit salary-note rule (misdirected
advice); byte-identity as the invariance claim (weakened to content-identity with
disclosed reorderings — by the script's own first run); the rows[0] register
citation; the manifest's false sorted-positions note (replaced by the true history).

**The day's finding, named by the operator.** Five instances of one pattern — a
claim about the artifact the artifact does not support — every one found by
inspecting the thing itself, every one behind a green test suite; the fifth caught
by the checking instrument checking itself. In the hot take as the turn.

**Next.** Sunday, in order, nothing before them: collision sweep (32 cases), QREPRO
from a fresh clone, final --split all. Then README fill, ambiguity-note grouping,
timing measurement 3, trajectories audit, video, submit.

**Session cost.** ~$7.90 today across ~25 runs and live demos (~$11.00 total).

### Post-close checkpoint 8 — Sixth instance: the run of record vs the DECISIONS claim

> **HUMAN: redirected** — three discrepancies. (1) eval/results/20260829-204901.md
> (the [11] run of record) carries two variants with a pairwise Delta while the
> always_abstain DECISIONS entry says the variant runs "by default alongside baseline
> and advanced". RESOLVED BY THE ARTIFACTS: 204901 was invoked with explicit
> "--variant baseline --variant advanced" flags (the G-4-literal habit used for every
> loop run); the flag-less default still runs all three — 20260829-210352, the same
> evening, shows three columns. The default never changed; the DECISIONS claim holds
> for default invocations. Standing orders: the final --split all run is flag-less so
> the trivial-abstention floor stands beside both solutions in the README headline
> table, and future measured runs use the default three-variant invocation — abstain
> costs nothing and its absence quietly removes the strongest part of the measurement
> story. (2) DATA.md said "30 cases" twice, present tense — same class as the
> manifest's sorted-positions claim; fixed to 32 with dated history. (3) The
> always_abstain entry's 30-case arithmetic stays as historical record; the current
> figure gets APPENDED once the final run lands, and every README floor number comes
> from that run, not the entry.
>
> Sweep executed across DATA.md, DECISIONS.md, PLAN.md, REPRODUCTION.md: two
> present-tense misses (both DATA.md, fixed); all other number hits are dated history
> or plan-era approximations, left intact by design. Guard added so the seventh
> instance fails the suite instead of waiting for eyes:
> test_committed_documents_state_the_true_case_counts pins present-tense counts in
> DATA.md and REPRODUCTION.md to the artifacts (red on the stale DATA.md, green after
> the fix). 95 tests.

### Post-close checkpoint 9 — Third dirty-tree incident: the guard

> **HUMAN: redirected** — tonight the guard only; everything under the README REVIEW
> heading is Sunday work after the final run. 20260829-210352 was produced with a
> dirty tree — the harness says so in the file — and is therefore unusable as a
> source of record: it does not reproduce from fd25c6e. Ordered: run_eval refuses to
> write a results file when the tree is dirty and --tag is set, printing the refusal
> before any model call is made rather than warning after the money is spent.
> Standing rule to submission: no number reaches README, CHANGELOG or the video from
> a run whose results file records git_dirty; check the field before citing any file.
>
> Audit before implementing: SIX of twenty committed results files record git_dirty —
> 20260828-224144 (Friday incident 1), 20260829-002446, 083304, 090655, and the two
> currently pasted into REPRODUCTION: 205909 (§5) and 210352 (§6). All six were
> tagged; the guard would have refused every one. 205818 (the §4 paste) is clean at
> the same SHA as the dirty 205909, so the tree went dirty between the §4 and §5
> runs — the §4 output was being pasted into REPRODUCTION.md while §5 ran. Sunday
> consequence queued: refresh the §5/§6 pastes from clean-tree runs after the final
> run lands.
>
> Red first: tests/test_run_eval.py, six tests, all failing (blocking_dirt did not
> exist). Implementation: blocking_dirt(porcelain) as a pure function; untracked
> files under eval/results/ are exempt because a fresh-clone verifier accumulates
> them by following REPRODUCTION in order, and refusing on the harness's own outputs
> would break CN-2 (DECISIONS entry, same date). Guard placed before load_cases, so
> refusal precedes any case read or model call. Exercised live against this change's
> own dirty tree before commit: exit 2, no results file written, no model call. 101
> tests green. Standing citation rule recorded in prompts/02 step 4; REPRODUCTION §6
> documents the refusal and §8 carries the troubleshooting row.

### Post-close checkpoint 10 — Sunday opens: the collision sweep

> **HUMAN: approved/ordered** — Sunday order as agreed, nothing before these three:
> collision sweep across the 32 cases, QREPRO from a fresh clone, flag-less
> --split all --tag final. Report the sweep before moving on. Standing constraint:
> a case whose resolution differs from its design assumption is repaired by renaming
> the fixture or correcting the label, never by tuning the resolver — that is the
> one repair that would invalidate the eval.
>
> Sweep built (eval/collision_sweep.py) and run: all 32 cases, mechanical, no model
> call. Clean on every dangerous class — 32/32 fixture orgs exact-self against
> 143,020 rows, 2/2 alias keys via alias_lookup (nothing preempted the alias pass),
> 3/3 asserted-absent names NoMatch, 22/22 dev recorded register paths MATCH their
> labels, holdout label-consistent (booleans only; trading_name_stated is
> final-run-only by nature). Two findings, one class: the group stems of the
> ambiguity cases match real register organisations — case-24 surfaces 11 candidates
> (2 fixture + 9 real 'Halcyon'), case-25 surfaces 3 (2 fixture + 1 real
> 'Merrivale'). Labels verified correct for the labelled reason in both.
>
> Repair: corrected the design record per the ruling — titles said "two entities",
> resolution says otherwise; renaming the fixtures was rejected (second snapshot
> rebuild on submission day, and CHANGELOG [8] already framed the collision as the
> real shape of the problem). Both design premises survive: routes still diverge
> across case-24's full set; case-25's candidates all hold Skilled Worker. Resolver
> untouched. Evidence: eval/results/collision-sweep-2026-08-30.md.

### Post-close checkpoint 11 — QREPRO from a fresh clone (2026-08-30)

> Executed literally in /tmp from a clone of dc7bc0c: python3.12 venv, pip install,
> cp .env.example (one variable, as documented), §7 gates first — 101 tests, mypy,
> ruff all green on the clean clone. §4 baseline: 0.3864 (paste says 0.2955; the doc
> predicts the difference and the committed band covers it). §5 advanced: every
> verdict-level metric identical to the paste — 0.9091 / 0.06667 / 0.9333 / 1 /
> 0.9886 / 1 / 0.9545. Demo CLI exercised on an improvised posting: end-to-end
> model→resolve→rules→render, register FAIL because the invented employer is
> genuinely absent — correct behaviour, not a defect. §6 flag-less: three columns,
> always_abstain 0.4886 exactly as pasted. The documented dirty-tree warning
> appeared from the second run onward exactly as §6 says.
>
> One finding, fixed: "expect your advanced column to match its paste exactly"
> overpromised — cost_per_case_usd moved in its final digit (0.00317 vs 0.003158,
> token-count jitter) and latency is the machine's. Sentence now scoped to
> verdict-level metrics. The §6 final command was not executed in the clone: it is
> the one-time official run, executed next in the main repo per the Sunday order.

### Post-close checkpoint 12 — Final run, breakdown, README

> Final run executed flag-less from a clean tree at ceb194d: all 32 cases, three
> variants, git_dirty=false, tag=final — eval/results/20260830-101148.json is the
> run of record. Advanced 0.9375 / baseline 0.5547 / floor 0.4844. The 10 held-out
> cases, never opened during development: verdict_utility 1.0 and every other
> metric at ceiling (final-breakdown-2026-08-30.md, derived mechanically from the
> per-case records by eval/split_breakdown.py — nothing re-run). The full set's one
> imperfection remains dev case-28, the priced B-rating cut. Baseline holdout 0.725
> was its friendliest subset — stated in README rather than hidden.
>
> Bookkeeping per the standing orders: abstention floor appended to the 2026-08-28
> DECISIONS entry (historical arithmetic untouched); REPRODUCTION §4/§5/§6 pastes
> refreshed from three fresh clean-tree runs with commits between them (101719,
> 101815, 102249 — all git_dirty=false; the superseded §5/§6 pastes had recorded
> dirty), final-run table added to §6; collision sweep regenerated against the run
> of record (22/22 recorded paths still MATCH). CHANGELOG [13] written.
>
> README filled with the four ordered corrections applied: sections reordered
> (user → bottleneck → value → prior art), headline table carries the floor beside
> both solutions with every number from 101148, hot take inverted to one paragraph
> leading with the invariance script, "and package.json" removed (no such file —
> checked), Licence picked (MIT + LICENSE file, register stays OGL v3), Agent setup
> table filled with the disclosure that the project was built through a coding
> agent under CLAUDE.md. One claim caught BEFORE commit this time: the dependency
> line initially said "anthropic, pydantic, rapidfuzz" from the plan's approval
> record — requirements.txt pins anthropic only (the implementation used
> dataclasses and its own token matching). The first pre-commit catch of the
> weekend's pattern; corrected against the artifact, with the entry-[1] figures
> (0.8, not the final 0.9091) likewise verified against the CHANGELOG before
> commit.

### Post-close checkpoint 13 — Ambiguity note grouped by route

> Operator-queued presentation fix, gated behind the sweep by design and executed
> after it validated the resolution: red test first (exact-string assertion on a
> 3-entity, 2-route synthetic), then assemble groups candidates under their licence
> route, largest group first, every entity still named — the disclosure principle
> from checkpoint [8] holds, the enumeration noise goes. Case-24 rendered live: ten
> Skilled Worker entities in one group, the GBM-only fixture alone in the other.
> Metrics provably unread (eval/metrics.py never touches uncertainty_notes) and
> measured unchanged anyway: 20260830-103559.json, advanced identical on every
> verdict-level metric. CHANGELOG [14].

---

## Session close 2026-08-30 (TR-5, final — supersedes the two Saturday closes)

**What changed since the last close.** The tagged-run dirty-tree guard (checkpoint
9); the collision sweep and the two ambiguity design-record corrections (checkpoint
10); QREPRO executed literally from a second fresh clone (checkpoint 11); the final
full-set run of record and its dev/holdout breakdown, REPRODUCTION pastes refreshed
from clean-tree runs, CHANGELOG [13], README completed with the four ordered
corrections plus LICENSE (checkpoint 12); the ambiguity note grouped by licence
route, CHANGELOG [14] (checkpoint 13).

**Which metric moved.** None by code today — Sunday's delta is measurement: the
final run (`eval/results/20260830-101148.json`, git_dirty=false, tag=final) put
advanced at verdict_utility 0.9375 / grounding 1.0 / confident_wrong 0.0455 on all
32 cases against baseline 0.5547 and the 0.4844 abstention floor, with the 10
never-opened holdout cases at ceiling on every metric.

**What was discarded and why.** Renaming the Halcyon/Merrivale fixtures to restore
the two-entity ambiguity design — the collisions are real register content and
renaming would have engineered away realistic behaviour at the cost of a second
snapshot rebuild on submission day (DECISIONS 2026-08-30). Executing the §6 final
command inside the QREPRO clone — it is the one-time official run and was executed
once, in the main repo, from a clean tree. A CHANGELOG entry for the guard —
harness tooling with no measured claim; DECISIONS and checkpoint 9 carry it.

**TR-1 note, stated rather than hidden.** Sunday's work continued in this file as
post-close checkpoints 9–13 because it is the same continued agent session as
Saturday's; this close is the file's final entry.

**Remaining, with the operator.** Timing measurement 3 (manual protocol), the
video, and submission. Approximate session cost 2026-08-30: ~$2.10 (QREPRO clone
runs, the final run, three clean-tree paste runs, the note-grouping run, one live
case-24 render); ~$13 for the competition to date.

### Post-close checkpoint 14 — Operator re-review applied; prompt 03 executed

> **HUMAN: redirected** — three orders. (1) The holdout caveat sharpened to the
> precise finding: baseline holdout is higher on verdicts (0.725 vs 0.4773) and
> LOWER on evidence quality (check_accuracy 0.75 vs 0.8409, grounding 0.9149 vs
> 0.9464) — easier at verdict level, harder at check level; README and CHANGELOG
> [13] now carry it. (2) PLAN.md gained a dated status block near the top: built as
> planned, contingencies that fired (B-rating cut priced by case-28; alias layer
> restored Saturday morning and shipped as synthetic fixtures, NOT the "cached
> Companies House lookups" the plan body describes — DATA.md authoritative), scope
> growth to 32 cases, final numbers; plan body deliberately unedited ("a plan that
> records its own divergence is worth more than one edited to look prescient").
> (3) Prompt 03 in full, then 04 and the video.
>
> Prompt 03 findings: secrets clean; effects clean (no network beyond the pinned
> model API, no writes outside the repo); baseline history clean (the one fix
> commit at 23:53 UTC precedes the 00:28 UTC freeze; zero commits after);
> determinism OK (three same-seed runs today, advanced identical); evidence
> integrity OK after tightening. TWO adversarial defects found and fixed red-first
> (CHANGELOG [15]): an empty posting produced a confident NOT_SPONSORABLE — NoMatch
> with nothing searched read as confirmed absence — now indeterminate/
> no_employer_stated; a binary file dumped a raw traceback — CLI now exits 2 typed.
> Post-fix run 20260830-105501: advanced identical on every metric. One WARNING
> stands: no input-size cap — an oversized posting is an oversized token bill;
> fix is a boundary cap in the CLI, priced but not built on final day.

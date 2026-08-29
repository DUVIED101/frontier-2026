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

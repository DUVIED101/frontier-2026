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

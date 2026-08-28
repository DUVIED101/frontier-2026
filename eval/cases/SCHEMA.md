# Evaluation case schema

One JSON file per case, `eval/cases/case-NN-<archetype-slug>.json`. Read by
`load_cases()` in `eval/run_eval.py`. `expected` is independently derived ground truth,
human-verified at the label gate (CLAUDE.md T-7) — never inferred from solver output, and
never trusted from the fixture prose alone.

## Top-level shape

```json
{
  "id": "case-01-compound-aggregator-gbm",
  "meta": { ... },
  "payload": { "requisition_text": "..." },
  "expected": { ... },
  "design_notes": "authoring commentary; ignored by the harness"
}
```

## `meta`

| Field | Type | Meaning |
|---|---|---|
| `archetype` | enum | One of the archetypes below. |
| `title` | string | One human-readable line for tables and the changelog. |
| `authored` | date | When the fixture was written. |
| `split` | `dev` \| `holdout` | **Holdout discipline, in force from the case-set commit:** while building the solution, do not open, read, quote, or reason about any file with `split: holdout`; run the eval with `--split dev` (the harness default) until the final Sunday run (`--split all`). Recalled holdout content gets recorded in the trajectory, not silently used. |
| `register_fixture_orgs` | string[] | Fictional organisation names this case expects in the register snapshot's appended fixture rows. **Empty array for `absent_all_aliases` cases** — absence is the ground truth. |
| `asserted_absent_names` | string[] (optional) | Names this case asserts are on NO row of the committed snapshot under any normalisation the resolver applies, and in no alias fixture. Used by absence cases (their employer) and by cases whose trap depends on a name being unlicensed (e.g. an agency in an aggregator wrapper). |

Archetype enum — the twelve from `docs/PLAN.md` §7, plus two added at the case-schema
review (`salary_below_going_rate`, `licence_rating_blocks`), plus two authoring additions
so every salary `reason` has at least one true case (`salary_straddles_floor`,
`salary_non_annual` — delete their cases at the label pass to veto):

`refusal_licensed` · `trading_name_gap` · `gbm_only` · `salary_below_floor` ·
`salary_below_going_rate` · `wrapper_contradiction` · `absent_all_aliases` ·
`clean_positive` · `clean_silent` · `salary_absent` · `ambiguous_group` ·
`rtw_boilerplate` · `licence_rating_blocks` · `salary_straddles_floor` ·
`salary_non_annual` · `compound_brand_gbm`

## `payload`

`requisition_text` only: the full page as the user would paste it, aggregator wrapper
included where the archetype calls for one. No employer hint — identifying the hiring
entity is part of the task under test. Both variants additionally read three repo-level
fixtures (identical inputs, per the fairness statement in `docs/PLAN.md` §4):

| Fixture | Path (locked now, lands in step 3) |
|---|---|
| Sponsor register snapshot (real, OGL) + appended fixture rows | `eval/cases/fixtures/sponsor-register-<YYYY-MM-DD>.csv.gz` |
| Fixture-row manifest (machine-readable; mirrored in `docs/DATA.md`) | `eval/cases/fixtures/register_fixture_rows.json` |
| Brand→legal-entity alias fixtures (Companies House lookups, cached offline) | `eval/cases/fixtures/aliases.json` |
| Salary floor config | `eval/cases/fixtures/floor_config.json` — see below |

**Floor config carries BOTH thresholds** (a Skilled Worker salary must clear the general
threshold AND the SOC going rate; the applicable floor is the maximum of the two):

```json
{
  "soc_code": "2134",
  "basis": "new_entrant",
  "general_threshold_gbp": { "amount": 33400, "effective_date": "...", "source_url": "..." },
  "going_rate_gbp":       { "amount": 38300, "effective_date": "...", "source_url": "..." },
  "counts_toward_floor":  { "policy": "guaranteed_basic_gross_annual_only", "source_url": "..." }
}
```

Data, not code. The going rate (£38,300) is operator-supplied ground truth; the general
threshold amount above is the authoring assumption and **must be verified against the
source at step 3** (re-checking cases 11 and 12, the closest to the boundary; if a
verified value moves a label, stop and report) — salary figures in the cases are chosen
with margin so a correction of ±£1,000 flips no label. `counts_toward_floor` states the
rule the whole salary check rests on: **only guaranteed basic gross annual pay counts**
toward either threshold — bonuses, profit share, equity, allowances and overtime do not.

## `expected`

```json
{
  "verdict": "SPONSORABLE | NOT_SPONSORABLE | UNVERIFIABLE",
  "determining_fact": "one sentence; becomes the report's lead sentence check",
  "register_snapshot_date": "YYYY-MM-DD",
  "checks": {
    "register":    { "status": "...", "reason": "..." },
    "route":       { "status": "...", "reason": "..." },
    "willingness": { "status": "...", "reason": "..." },
    "salary":      { "status": "...", "reason": "..." }
  },
  "evidence_anchors": { ... }
}
```

`register_snapshot_date` is the snapshot date these labels were verified against. The
solver must report the date of the snapshot it actually read; the two must agree
(`test_output_snapshot_date_matches_expected`), and the report's staleness warning is
checked against it. Authoring placeholder is `2026-08-28`; if the fetched snapshot's
published date differs at step 3, one bulk update fixes every case and the config before
any eval run — no results exist yet, so nothing becomes incomparable.

**`status` is uniform tri-state on every check:** `pass` | `fail` | `indeterminate`.
The verdict combinator is fixed by `docs/PLAN.md` §2: any `fail` → NOT_SPONSORABLE;
all `pass` → SPONSORABLE; otherwise UNVERIFIABLE.

**`reason` is per-check fine grain** (label detail; feeds the report and the tests):

| Check | Reasons |
|---|---|
| `register` | `legal_name_exact` · `trading_name_stated` (tie stated in posting) · `alias_lookup` (tie only via alias fixture) · `no_match` · `ambiguous_group` |
| `route` | `skilled_worker` · `gbm_only` · `other_routes_only` · `rating_blocks_cos` (route present but the licence rating means no new CoS can be issued) · `no_entity` (register not `pass`, so routes unreadable) |
| `willingness` | `offered` · `refused` · `silent` · `boilerplate_ambiguous` |
| `salary` | `above_floor` (≥ both thresholds) · `below_general_threshold` (salary < general threshold) · `below_going_rate` (clears general threshold, below SOC going rate) · `straddles_floor` (stated range spans the applicable floor) · `absent` · `non_annual_unclear` |

Status↔reason mappings are fixed: `gbm_only`, `rating_blocks_cos`,
`below_general_threshold` and `below_going_rate` are always `fail`; `silent` and
`boilerplate_ambiguous` are always `indeterminate` (the C3 silence policy); `no_match` is
`fail` only because ground truth knows the alias pass found nothing (C1 policy);
`straddles_floor`, `absent`, `non_annual_unclear` and `no_entity` are always
`indeterminate`.

**`evidence_anchors`** — machine-checkable anchors, present where the archetype makes
them crisp; used by tests and the label pass, not by `check_accuracy`:

| Anchor | Shape |
|---|---|
| `register_row` | `{organisation_name, town_city, type_rating, route}` — must match the appended fixture row verbatim once step 3 commits it. |
| `alias` | `{brand, registered_name, source: "companies_house_fixture"}` |
| `willingness_quote` | Exact substring of `requisition_text` that settles the stance. |
| `salary_text` | Exact substring stating the salary. |

## Fixture-integrity tests (named now, land in step 3 with the snapshot)

- `test_fixture_orgs_do_not_collide_with_real_register` — no appended fictional
  organisation matches any real row of the snapshot under the resolver's normalisations.
- `test_asserted_absent_names_match_no_row_under_any_normalisation` — the absence check
  run the other way: every name in any case's `asserted_absent_names` matches **no row of
  the committed snapshot** (real or fixture) under any normalisation the resolver
  applies, and appears in no alias fixture. Absence ground truth is verified against the
  actual committed artefact, not assumed from fiction.

Either test failing at step 3 forces a fixture rename before anything runs.

## Scoring hooks (metric contract, lands in step 4)

- `check_accuracy` compares the four `status` fields only.
- `exact_match` subset-compares every key present in `expected` (so `reason` is scored
  strictly wherever a case carries it). **Labelling lever:** deleting a `reason` from a
  case's `expected` during the label pass relaxes that case to status-only strictness.
- `verdict_utility` reads `verdict` alone: +1.0 correct (UNVERIFIABLE is *correct* when
  ground truth is UNVERIFIABLE); +0.25 UNVERIFIABLE where truth was determinable; −1.0
  confident wrong.
- `grounding_rate` needs no anchors — it mechanically verifies the *solver's* citations
  (quote is a verbatim substring of `requisition_text`; cited register row exists in the
  snapshot).

## Solver output contract (both variants; the harness compares like with like)

```json
{
  "verdict": "...",
  "determining_fact": "...",
  "checks": {
    "<check>": {
      "status": "...", "reason": "...",
      "evidence": { "quote": "...", "offset": 0, "register_row": { ... } }
    }
  },
  "uncertainty": "what could not be established and what it would take to establish it",
  "register_snapshot_date": "YYYY-MM-DD"
}
```

`evidence` fields are optional per check but everything cited must ground mechanically —
uncited claims cost nothing here and everything in `grounding_rate`.

## Labelling conventions (for the label-correction pass)

1. Ground truth is what a careful human establishes **from the fixture text plus the
   fixtures above** — not what the archetype intended. If the prose accidentally
   under-determines the label, fix the prose or the label, and say which in
   `design_notes`.
2. `silent` vs `boilerplate_ambiguous`: `silent` = the posting does not touch the topic;
   `boilerplate_ambiguous` = it touches it without settling it ("must have the right to
   work in the UK"). Both are `indeterminate`; the distinction changes only the report's
   advice line.
3. Salary figures are deliberate relative to the two thresholds (authoring assumption:
   general £33,400 — **verify**; going rate £38,300 — operator-supplied): clear-above ≥
   £39,500; clear-below-both ≤ £30,000; between-band £35,000–£37,500; straddling ranges
   span £38,300 with the lower bound safely above the general threshold. No accidental
   near-misses.
3a. Only **guaranteed basic gross annual pay** counts toward the thresholds; bonuses,
   profit share, equity, allowances and overtime are excluded (`counts_toward_floor`).
   Labels compare the base figure alone, and extraction (baseline prompt and advanced
   schema alike) must separate base pay from non-guaranteed components rather than
   parsing one number. Several cases carry non-guaranteed extras as bait by design.
4. In `wrapper_contradiction` cases the posting **body** is the primary source; wrapper
   metadata that contradicts it does not change ground truth.
5. Every case must be decidable by a human with the committed fixtures alone — if
   deciding it needs the live web, the case is wrong (the eval never touches the
   network).

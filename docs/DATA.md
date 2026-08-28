# Data provenance

Only public or synthetic data is used (CLAUDE.md CN-7). Generated fixtures are preferred.

| Dataset | Source | Licence | How obtained | Used for |
|---|---|---|---|---|
| Register of licensed sponsors: workers (snapshot 2026-08-28) | [Publication page](https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers) · [CSV asset](https://assets.publishing.service.gov.uk/media/6a91566801bbff0bf8f97b48/SP_-_Worker_and_Temporary_Worker_Web_Register_-_2026-08-28.csv) | OGL v3.0 | `curl` on 2026-08-28 | `register` and `route` checks; entity resolution |
| Skilled Worker salary thresholds | [How much you'll be paid](https://www.gov.uk/skilled-worker-visa/how-much-youll-be-paid) · [Going rates table](https://www.gov.uk/government/publications/skilled-worker-visa-going-rates-for-eligible-occupations/skilled-worker-visa-going-rates-for-eligible-occupation-codes) | OGL v3.0 | GOV.UK content API on 2026-08-28 | `salary` check (`floor_config.json`) |
| Synthetic requisition fixtures (30 cases) | Authored in-repo | Original work | See "Synthetic fixtures" | All four checks |
| Synthetic alias fixtures | Authored in-repo | Original work | `eval/cases/fixtures/aliases.json` | Trading-name resolution |

Contains public sector information licensed under the
[Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

## The register snapshot: real rows + fixture rows

`eval/cases/fixtures/sponsor-register-2026-08-28.csv.gz` holds the **complete, unfiltered**
official register retrieved on 2026-08-28 — **142,988 real rows, byte-identical to the
source asset** — plus **30 fictional sponsor rows** for the fictional employers in the
evaluation cases. Nothing was removed; the gzipped file is ~2.0 MB, well inside the 50 MB
submission limit, so no filtering was needed.

**How to tell real rows from fixture rows:** the machine-readable manifest
`eval/cases/fixtures/register_fixture_rows.json` is the single, complete list of fixture
rows; every other row is the real register. The 30 fictional organisations:

Arkenfield Systems Ltd · Ashcombe Digital Ltd · Bryelock Systems Ltd · Duncastle Tech Ltd ·
Elvermere Systems Ltd · Farrowgate Analytics Ltd · Ferrowdale Cloud Ltd ·
Halcyon Consulting (UK) Ltd · Halcyon Technologies Ltd · Hazelmoor Interactive Ltd ·
Kestrel Dynamics Ltd · Larchdown Consulting Ltd · Marlowe & Finch Technology Ltd ·
Merrivale Software Ltd · Merrivale Studios Ltd · Nordwick Data Ltd ·
Ondrell Technologies Ltd · Ostermere Technologies Ltd · Pellbrook Digital Ltd ·
Quenby Applications Ltd · Quillstone Apps Ltd · Redegate Software Ltd ·
Silverbeck Software Ltd · Stonebridge Softworks Ltd · Tarnbrook Software Ltd ·
Thornber Computing Ltd · Veltrix Software Ltd · Windlecombe Software Ltd ·
Wrenfield Payments Ltd · Wrexfell Digital Ltd

**Fixture rows are deliberately in-band-unmarked and shape-indistinguishable** (same
columns, same CRLF endings, values drawn from the real file's exact vocabulary, counties
following each town's real fill pattern, rows inserted at name-sorted positions rather
than appended). Reason, from the design review: if a solver could learn "fixture rows
look like X", the register check would pass on an artifact rather than on the data, and
every register number in the evaluation would be worthless. Verified by
`tests/test_fixture_integrity.py::test_fixture_rows_are_shape_indistinguishable` plus a
sampled comparison: every fixture row's field-feature class is one of the two most common
real-row classes (35% and 18% of real rows respectively).

**Absence is verified both ways.** Three names are asserted to match **no** row of the
committed snapshot under the resolver's normalisations and no alias fixture: Copperwaite
Studio, Glimmerforth Labs, TalentBridge Recruitment. Tests:
`test_fixture_orgs_do_not_collide_with_real_register` and
`test_asserted_absent_names_match_no_row_under_any_normalisation`.

## Salary thresholds (`floor_config.json`), verified 2026-08-28

- **General threshold (new entrant): £33,400** — stated by the live GOV.UK pay page.
- **Going rate (SOC 2134, new entrant): £38,300** — the going-rates table (updated
  2025-07-22) lists the SOC 2134 standard rate as **£54,700**; a new entrant may be paid
  70% of the standard going rate (minimum the general threshold): 0.7 × 54,700 = 38,290,
  rounded to the nearest £100 per the published convention. The operator-supplied working
  figure was confirmed against this computation. No evaluation label sits within £700 of
  the boundary.
- **What counts:** only guaranteed basic gross annual pay counts toward either threshold;
  bonuses, profit share, equity, options, allowances and overtime do not
  (`counts_toward_floor`). Annual rates are based on a 37.5-hour week and pro-rated
  otherwise; labels in this evaluation use the stated annual base salary.

### Finding: the official going-rates table carries a trap column for exactly this user

This is a finding of the project, not a footnote. The going-rates table shows two figures
for SOC 2134: the standard rate (£54,700) and a **"Lower going rate" of £40,000**. Read
without its header qualification — which lives in prose above the table — the £40,000
column looks like the discounted floor for a new entrant. It is not: it applies **only**
to Health and Care Worker visas and to transitional holders whose first CoS predates
4 April 2024. The actual new-entrant floor is 70% of the standard rate (£38,290 →
£38,300), a figure that appears **nowhere in the table** and must be derived.

An early-career applicant checking their own eligibility against the primary source will
meet a wrong-but-official-looking number that differs from their true floor by £1,700 —
enough to wrongly disqualify a £39,000 offer. The failure mode this system exists to
prevent — a confidently wrong sponsorability conclusion drawn from a correctly retrieved
but misread source — appears in the government's own reference table. This was
encountered live during threshold verification (see the step-3 trajectory: it nearly
triggered a stop on case-16's label) and is why `floor_config.json` records the full
derivation and why the verification report cites which rules snapshot it applied.

## Synthetic fixtures

Authored, not generated: the 30 requisition cases were written by hand against the
archetype matrix in `docs/PLAN.md` §7 and label-verified at two human gates (schema
review and label-correction — see the trajectory), satisfying CLAUDE.md T-7. They are
committed and never regenerated, so no seed or generator is required to reproduce any
result. Company names, postings, people and brands are fictional; structural patterns
(trading-name gaps, GBM-only licences, refusal wording, threshold-straddling salaries)
reproduce real patterns the author has personally encountered and documented.

The alias fixtures (`aliases.json`) are likewise synthetic, mirroring the *shape* of
Companies House trading-name records for the fictional brands; no real Companies House
data is included.

## Personal data

None. No real personal data enters this repository at any point. Requisition fixtures
name no real person; the register snapshot contains organisation-level public data only.

# Collision sweep — designed employer strings vs the committed snapshot

Snapshot: `sponsor-register-2026-08-28.csv.gz` (143020 rows). Recorded-path column (dev only): `20260829-210352.json`. Mechanical throughout — no model call. Holdout cases: counts and booleans only.

- `case-01-compound-aggregator-gbm` (dev): orgs 1/1 exact-self · aliases 1/1 alias_lookup · label pass/alias_lookup; recorded MATCH
- `case-02-refusal-licensed` (dev): orgs 1/1 exact-self · label pass/legal_name_exact; recorded MATCH
- `case-03-refusal-licensed-hedged` (holdout): orgs 1/1 exact-self · label-consistent: True
- `case-04-trading-name-alias` (dev): orgs 1/1 exact-self · aliases 1/1 alias_lookup · label pass/alias_lookup; recorded MATCH
- `case-05-trading-name-stated` (holdout): orgs 1/1 exact-self · label-consistent: final-run-only
- `case-06-trading-name-stated-offered` (dev): orgs 1/1 exact-self · label pass/trading_name_stated; recorded MATCH
- `case-07-gbm-only-offered` (dev): orgs 1/1 exact-self · label pass/legal_name_exact; recorded MATCH
- `case-08-gbm-only-silent` (holdout): orgs 1/1 exact-self · label-consistent: True
- `case-09-salary-below-both` (dev): orgs 1/1 exact-self · label pass/legal_name_exact; recorded MATCH
- `case-10-salary-range-below-both` (holdout): orgs 1/1 exact-self · label-consistent: True
- `case-11-salary-below-going-rate` (dev): orgs 1/1 exact-self · label pass/legal_name_exact; recorded MATCH
- `case-12-salary-range-below-going-rate` (holdout): orgs 1/1 exact-self · label-consistent: True
- `case-13-wrapper-salary-contradiction` (dev): orgs 1/1 exact-self · label pass/legal_name_exact; recorded MATCH
- `case-14-wrapper-agency-contradiction` (holdout): orgs 1/1 exact-self · absent 1/1 NoMatch · label-consistent: True
- `case-15-absent-offered` (dev): orgs 0/0 exact-self · absent 1/1 NoMatch · label fail/no_match; recorded MATCH
- `case-16-absent-silent` (holdout): orgs 0/0 exact-self · absent 1/1 NoMatch · label-consistent: True
- `case-17-clean-positive` (dev): orgs 1/1 exact-self · label pass/legal_name_exact; recorded MATCH
- `case-18-clean-positive-range` (dev): orgs 1/1 exact-self · label pass/legal_name_exact; recorded MATCH
- `case-19-clean-positive-third` (holdout): orgs 1/1 exact-self · label-consistent: True
- `case-20-clean-silent` (dev): orgs 1/1 exact-self · label pass/legal_name_exact; recorded MATCH
- `case-21-clean-silent-range` (holdout): orgs 1/1 exact-self · label-consistent: True
- `case-22-salary-absent-offered` (dev): orgs 1/1 exact-self · label pass/legal_name_exact; recorded MATCH
- `case-23-salary-absent-silent` (holdout): orgs 1/1 exact-self · label-consistent: True
- `case-24-ambiguous-group-diverging` (dev): orgs 2/2 exact-self · group-stem -> Ambiguous 11 orgs (2 fixture + 9 real; designed 2) · label indeterminate/ambiguous_group; recorded MATCH
- `case-25-ambiguous-group-same-route` (dev): orgs 2/2 exact-self · group-stem -> Ambiguous 3 orgs (2 fixture + 1 real; designed 2) · label indeterminate/ambiguous_group; recorded MATCH
- `case-26-rtw-boilerplate` (dev): orgs 1/1 exact-self · label pass/legal_name_exact; recorded MATCH
- `case-27-rtw-boilerplate-plus-refusal` (dev): orgs 1/1 exact-self · label pass/legal_name_exact; recorded MATCH
- `case-28-rating-blocks-cos` (dev): orgs 1/1 exact-self · label pass/legal_name_exact; recorded MATCH
- `case-29-salary-straddles` (dev): orgs 1/1 exact-self · label pass/legal_name_exact; recorded MATCH
- `case-30-salary-day-rate` (dev): orgs 1/1 exact-self · label pass/legal_name_exact; recorded MATCH
- `case-31-wrapped-quote-offered` (dev): orgs 1/1 exact-self · label pass/legal_name_exact; recorded MATCH
- `case-32-multi-route-entity` (dev): orgs 1/1 exact-self · label pass/legal_name_exact; recorded MATCH

## Findings (2)
- case-24-ambiguous-group-diverging: designed 2-entity ambiguity actually surfaces 11 candidates — 9 real register organisations share the group stem 'halcyon'
- case-25-ambiguous-group-same-route: designed 2-entity ambiguity actually surfaces 3 candidates — 1 real register organisation shares the group stem 'merrivale'

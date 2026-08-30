# Split breakdown — same per-case records, same metric definitions

Derived from `20260830-101148.json` (commit `ceb194d`, git_dirty=False, tag `final`); nothing re-run.

## baseline

| Metric | all | dev | holdout |
|---|---|---|---|
| verdict_utility | 0.5547 | 0.4773 | 0.725 |
| confident_wrong_rate | 0.2609 | 0.3125 | 0.1429 |
| decisive_accuracy | 0.7391 | 0.6875 | 0.8571 |
| decisive_rate | 0.8636 | 0.8667 | 0.8571 |
| check_accuracy | 0.8125 | 0.8409 | 0.75 |
| grounding_rate | 0.9371 | 0.9464 | 0.9149 |
| cost_per_case_usd | 0.01118 | 0.01126 | 0.01099 |
| exact_match | 0 | 0 | 0 |
| error_rate | 0 | 0 | 0 |
| p50_seconds | 9.652 | 9.63 | 9.725 |
| p95_seconds | 12.36 | 12.9 | 10.86 |

Cases: 32 all / 22 dev / 10 holdout.

## always_abstain

| Metric | all | dev | holdout |
|---|---|---|---|
| verdict_utility | 0.4844 | 0.4886 | 0.475 |
| confident_wrong_rate | 0 | 0 | 0 |
| decisive_accuracy | 0 | 0 | 0 |
| decisive_rate | 0 | 0 | 0 |
| check_accuracy | 0 | 0 | 0 |
| grounding_rate | 0 | 0 | 0 |
| cost_per_case_usd | 0 | 0 | 0 |
| exact_match | 0 | 0 | 0 |
| error_rate | 0 | 0 | 0 |
| p50_seconds | 1.67e-07 | 1.67e-07 | 1.66e-07 |
| p95_seconds | 5e-07 | 5.41e-07 | 2.08e-07 |

Cases: 32 all / 22 dev / 10 holdout.

## advanced

| Metric | all | dev | holdout |
|---|---|---|---|
| verdict_utility | 0.9375 | 0.9091 | 1 |
| confident_wrong_rate | 0.04545 | 0.06667 | 0 |
| decisive_accuracy | 0.9545 | 0.9333 | 1 |
| decisive_rate | 1 | 1 | 1 |
| check_accuracy | 0.9922 | 0.9886 | 1 |
| grounding_rate | 1 | 1 | 1 |
| cost_per_case_usd | 0.003142 | 0.003161 | 0.003099 |
| exact_match | 0.9688 | 0.9545 | 1 |
| error_rate | 0 | 0 | 0 |
| p50_seconds | 2.099 | 2.154 | 2.008 |
| p95_seconds | 3.38 | 3.507 | 2.4 |

Cases: 32 all / 22 dev / 10 holdout.


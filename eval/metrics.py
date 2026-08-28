"""Metric definitions for frontier-2026.

This module is the contract. Every number in README.md and CHANGELOG.md is produced
by a Metric defined here, so a metric definition may not change silently: if one does
change, previous results become incomparable and that must be recorded in
docs/DECISIONS.md and stated in the affected CHANGELOG entry.

Add the problem-specific metrics once the challenge statement is published. Keep the
three generic ones — correctness, error rate and latency are meaningful for any task
and give the baseline something to be beaten on from the first run.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class CaseResult:
    case_id: str
    output: dict[str, Any]
    expected: dict[str, Any]
    seconds: float
    error: str | None = None


@dataclass
class Metric:
    name: str
    description: str
    higher_is_better: bool
    aggregate: Callable[[list[CaseResult]], float]
    unit: str = ""


# --------------------------------------------------------------------------
# Generic metrics — valid on day one, before the problem is known
# --------------------------------------------------------------------------


def _exact_match(results: list[CaseResult]) -> float:
    scored = [r for r in results if r.expected]
    if not scored:
        return 0.0
    hits = sum(1 for r in scored if not r.error and r.output == r.expected)
    return hits / len(scored)


def _error_rate(results: list[CaseResult]) -> float:
    return (sum(1 for r in results if r.error) / len(results)) if results else 0.0


def _p50_latency(results: list[CaseResult]) -> float:
    return statistics.median(r.seconds for r in results) if results else 0.0


def _p95_latency(results: list[CaseResult]) -> float:
    if not results:
        return 0.0
    ordered = sorted(r.seconds for r in results)
    idx = min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1))))
    return ordered[idx]


METRICS: list[Metric] = [
    Metric(
        name="exact_match",
        description="Fraction of cases where output equals the independently derived expectation.",
        higher_is_better=True,
        aggregate=_exact_match,
    ),
    Metric(
        name="error_rate",
        description="Fraction of cases that raised. A crash is a measurable outcome, not a skip.",
        higher_is_better=False,
        aggregate=_error_rate,
    ),
    Metric(
        name="p50_seconds",
        description="Median wall-clock time per case.",
        higher_is_better=False,
        aggregate=_p50_latency,
        unit="s",
    ),
    Metric(
        name="p95_seconds",
        description="95th percentile wall-clock time per case. Tail behaviour, not the average.",
        higher_is_better=False,
        aggregate=_p95_latency,
        unit="s",
    ),
]


# --------------------------------------------------------------------------
# Problem-specific metrics — ADD AFTER KICKOFF
# --------------------------------------------------------------------------
# Guidance, learned before the problem was known:
#   - At least one metric must map directly to a stated acceptance criterion.
#   - At least one must capture a failure mode the baseline exhibits, otherwise
#     the advanced solution has nothing to demonstrate.
#   - Prefer metrics that are cheap to compute and impossible to game by hardcoding
#     the fixtures.
#   - If a metric cannot be computed deterministically, report its variance instead
#     of pretending it is a point estimate (run_eval.py --repeats).

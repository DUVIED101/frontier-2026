"""Metric definitions for frontier-2026.

This module is the contract. Every number in README.md and CHANGELOG.md is produced
by a Metric defined here, so a metric definition may not change silently: if one does
change, previous results become incomparable and that must be recorded in
docs/DECISIONS.md and stated in the affected CHANGELOG entry.

Problem-specific metrics for Skilled Worker sponsorship verification, per docs/PLAN.md
§6. The asymmetry is deliberate and central: a confident wrong verdict scores 1.25
below an honest abstention (`verdict_utility`), because a wasted application costs the
user more than a manual re-check. `exact_match` was narrowed to a subset comparison
before the baseline freeze (DECISIONS.md 2026-08-28): label-only fields
(`determining_fact`, `evidence_anchors`) are excluded — they are verified by dedicated
tests and by `grounding_rate`, not echoed by solvers. `decisive_accuracy` and
`decisive_rate` were added 2026-08-29, also before the freeze, with a pre-registered
target for the advanced variant (DECISIONS.md); the one prior recorded run predates
them and is superseded by the defect-fix rerun regardless.
"""

from __future__ import annotations

import csv
import functools
import gzip
import io
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

VERDICTS = ("SPONSORABLE", "NOT_SPONSORABLE", "UNVERIFIABLE")
ABSTAIN = "UNVERIFIABLE"
DEFINITIVE_VERDICTS = ("SPONSORABLE", "NOT_SPONSORABLE")
CHECKS = ("register", "route", "willingness", "salary")

UTILITY_CORRECT = 1.0
UTILITY_SAFE_ABSTENTION = 0.25
UTILITY_CONFIDENT_WRONG = -1.0
UTILITY_NO_VERDICT = 0.0

# Source: Anthropic model price table (reference cached 2026-06-04, checked 2026-08-28);
# recorded with the model decision in DECISIONS.md.
MODEL_PRICES_USD_PER_MTOK: dict[str, dict[str, float]] = {
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
}

# Fields present in expected for labelling, tests and the report — never echoed by a
# solver, so excluded from exact_match's subset comparison.
_LABEL_ONLY_FIELDS = ("determining_fact", "evidence_anchors")

_FIXTURES_DIR = Path(__file__).resolve().parent / "cases" / "fixtures"


@dataclass
class CaseResult:
    case_id: str
    output: dict[str, Any]
    expected: dict[str, Any]
    seconds: float
    error: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class Metric:
    name: str
    description: str
    higher_is_better: bool
    aggregate: Callable[[list[CaseResult]], float]
    unit: str = ""


# --------------------------------------------------------------------------
# Problem-specific metrics — Skilled Worker sponsorship verification
# --------------------------------------------------------------------------


def _verdict(r: CaseResult) -> str | None:
    v = r.output.get("verdict") if isinstance(r.output, dict) else None
    return v if v in VERDICTS else None


def _verdict_utility(results: list[CaseResult]) -> float:
    scored = [r for r in results if r.expected.get("verdict")]
    if not scored:
        return 0.0

    def score(r: CaseResult) -> float:
        out = _verdict(r)
        if out is None:
            return UTILITY_NO_VERDICT
        if out == r.expected["verdict"]:
            return UTILITY_CORRECT
        if out == ABSTAIN:
            return UTILITY_SAFE_ABSTENTION
        return UTILITY_CONFIDENT_WRONG

    return sum(score(r) for r in scored) / len(scored)


def _confident_wrong_rate(results: list[CaseResult]) -> float:
    definitive = [
        r
        for r in results
        if r.expected.get("verdict") and _verdict(r) not in (None, ABSTAIN)
    ]
    if not definitive:
        return 0.0
    wrong = sum(1 for r in definitive if _verdict(r) != r.expected["verdict"])
    return wrong / len(definitive)


def _decisive_accuracy(results: list[CaseResult]) -> float:
    """Correct definitive verdicts ÷ definitive verdicts issued.

    Added 2026-08-29, before the baseline freeze (DECISIONS.md): paired with
    decisive_rate so a variant cannot pass verdict_utility by drifting toward
    abstention. A definitive verdict where the truth is UNVERIFIABLE counts as wrong.
    """
    definitive = [
        r
        for r in results
        if r.expected.get("verdict") and _verdict(r) in DEFINITIVE_VERDICTS
    ]
    if not definitive:
        return 0.0
    correct = sum(1 for r in definitive if _verdict(r) == r.expected["verdict"])
    return correct / len(definitive)


def _decisive_rate(results: list[CaseResult]) -> float:
    """Definitive verdicts issued on determinable cases ÷ determinable cases.

    always_abstain scores 0 by construction — that is the point: the pre-registered
    target (DECISIONS.md 2026-08-29) requires advanced to beat always_abstain here
    while holding decisive_accuracy high, so abstention cannot masquerade as skill.
    """
    determinable = [
        r for r in results if r.expected.get("verdict") in DEFINITIVE_VERDICTS
    ]
    if not determinable:
        return 0.0
    issued = sum(1 for r in determinable if _verdict(r) in DEFINITIVE_VERDICTS)
    return issued / len(determinable)


def _check_accuracy(results: list[CaseResult]) -> float:
    scored = [r for r in results if isinstance(r.expected.get("checks"), dict)]
    if not scored:
        return 0.0

    def per_case(r: CaseResult) -> float:
        out_checks = r.output.get("checks") if isinstance(r.output, dict) else None
        out_checks = out_checks if isinstance(out_checks, dict) else {}
        expected_checks = r.expected["checks"]
        hits = 0
        for name, exp in expected_checks.items():
            got = out_checks.get(name)
            if isinstance(got, dict) and got.get("status") == exp.get("status"):
                hits += 1
        return hits / len(expected_checks)

    return sum(per_case(r) for r in scored) / len(scored)


@functools.lru_cache(maxsize=1)
def _snapshot_rows() -> frozenset[tuple[str, str, str, str]]:
    matches = sorted(_FIXTURES_DIR.glob("sponsor-register-*.csv.gz"))
    if not matches:
        raise FileNotFoundError(f"no register snapshot under {_FIXTURES_DIR}")
    text = gzip.decompress(matches[-1].read_bytes()).decode("utf-8-sig")
    return frozenset(
        (r["Organisation Name"], r["Town/City"], r["Type & Rating"], r["Route"])
        for r in csv.DictReader(io.StringIO(text))
    )


def _grounding_rate(results: list[CaseResult]) -> float:
    """Citations verified mechanically ÷ citations issued.

    A quote grounds iff it is a verbatim substring of the case's requisition text; a
    cited register row grounds iff it exists in the committed snapshot. Zero citations
    scores 0 — evidence-free output is ungrounded by definition.
    """
    issued = 0
    verified = 0
    for r in results:
        checks = r.output.get("checks") if isinstance(r.output, dict) else None
        if not isinstance(checks, dict):
            continue
        source = str(r.payload.get("requisition_text", ""))
        for check in checks.values():
            if not isinstance(check, dict):
                continue
            evidence = check.get("evidence")
            if not isinstance(evidence, dict):
                continue
            quote = evidence.get("quote")
            if isinstance(quote, str) and quote:
                issued += 1
                verified += quote in source
            row = evidence.get("register_row")
            if isinstance(row, dict):
                issued += 1
                key = (
                    row.get("organisation_name"),
                    row.get("town_city"),
                    row.get("type_rating"),
                    row.get("route"),
                )
                verified += key in _snapshot_rows()
    return verified / issued if issued else 0.0


def _cost_per_case_usd(results: list[CaseResult]) -> float:
    if not results:
        return 0.0
    total = 0.0
    for r in results:
        usage = r.output.get("_usage") if isinstance(r.output, dict) else None
        if not isinstance(usage, dict):
            continue
        prices = MODEL_PRICES_USD_PER_MTOK[str(usage["model"])]
        total += (
            float(usage["input_tokens"]) * prices["input"]
            + float(usage["output_tokens"]) * prices["output"]
        ) / 1_000_000
    return total / len(results)


# --------------------------------------------------------------------------
# Generic metrics — kept from the pre-kickoff harness
# --------------------------------------------------------------------------


def _subset_match(expected: Any, actual: Any) -> bool:
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            _subset_match(v, actual.get(k)) for k, v in expected.items()
        )
    return bool(expected == actual)


def _exact_match(results: list[CaseResult]) -> float:
    """Strict subset agreement on every comparable key expected carries.

    Narrowed from whole-dict equality before the baseline freeze (DECISIONS.md
    2026-08-28). Label-only fields are excluded; everything else in expected —
    verdict, per-check status and (where a case carries it) reason, snapshot date —
    must match the output exactly. Deleting a `reason` from a case's expected relaxes
    that case to status-only strictness (SCHEMA.md labelling lever).
    """
    scored = [r for r in results if r.expected]
    if not scored:
        return 0.0
    hits = 0
    for r in scored:
        comparable = {
            k: v for k, v in r.expected.items() if k not in _LABEL_ONLY_FIELDS
        }
        hits += not r.error and _subset_match(comparable, r.output)
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
        name="verdict_utility",
        description=(
            "Primary. Per case: +1.0 correct verdict (including UNVERIFIABLE where "
            "ground truth is unverifiable); +0.25 UNVERIFIABLE where truth was "
            "determinable; -1.0 confident wrong; 0.0 no valid verdict. Mean, range "
            "[-1, 1]."
        ),
        higher_is_better=True,
        aggregate=_verdict_utility,
    ),
    Metric(
        name="confident_wrong_rate",
        description=(
            "Wrong verdicts ÷ cases where the system issued a definitive "
            "SPONSORABLE/NOT_SPONSORABLE."
        ),
        higher_is_better=False,
        aggregate=_confident_wrong_rate,
    ),
    Metric(
        name="decisive_accuracy",
        description=(
            "Correct definitive verdicts ÷ definitive verdicts issued. Definitive "
            "answers on UNVERIFIABLE truth count as wrong."
        ),
        higher_is_better=True,
        aggregate=_decisive_accuracy,
    ),
    Metric(
        name="decisive_rate",
        description=(
            "Definitive verdicts issued on determinable cases ÷ determinable cases. "
            "always_abstain scores 0 by construction; abstention cannot masquerade "
            "as improvement."
        ),
        higher_is_better=True,
        aggregate=_decisive_rate,
    ),
    Metric(
        name="check_accuracy",
        description=(
            "Macro-average agreement of the four per-check statuses with the "
            "per-check labels. The per-stage diagnostic."
        ),
        higher_is_better=True,
        aggregate=_check_accuracy,
    ),
    Metric(
        name="grounding_rate",
        description=(
            "Mechanically verified citations ÷ citations issued: quotes must appear "
            "verbatim in the posting, cited register rows must exist in the snapshot."
        ),
        higher_is_better=True,
        aggregate=_grounding_rate,
    ),
    Metric(
        name="cost_per_case_usd",
        description="Mean USD per case from reported token usage at pinned prices.",
        higher_is_better=False,
        aggregate=_cost_per_case_usd,
        unit="USD",
    ),
    Metric(
        name="exact_match",
        description=(
            "Fraction of cases whose output matches every comparable expected key "
            "exactly (subset match; label-only fields excluded)."
        ),
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

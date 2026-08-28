"""Unit tests for the problem-specific metric definitions in eval/metrics.py.

Every expectation is hand-computed, never derived from the aggregate under test (T-7).
CaseResults are constructed directly so each aggregate is exercised on known inputs.
The register-row grounding test reads the committed snapshot fixture — the same
artefact the eval itself uses.
"""

from __future__ import annotations

from typing import Any

from eval.metrics import METRICS, CaseResult

EXPECTED_METRIC_NAMES = {
    "verdict_utility",
    "confident_wrong_rate",
    "check_accuracy",
    "grounding_rate",
    "cost_per_case_usd",
    "exact_match",
    "error_rate",
    "p50_seconds",
    "p95_seconds",
}

POSTING = "Software Engineer at Farrowgate.\nWe offer visa sponsorship. Salary £41,000."

EXPECTED_NS: dict[str, Any] = {
    "verdict": "NOT_SPONSORABLE",
    "determining_fact": "label-only field; never echoed by a solver",
    "register_snapshot_date": "2026-08-28",
    "checks": {
        "register": {"status": "pass", "reason": "legal_name_exact"},
        "route": {"status": "pass", "reason": "skilled_worker"},
        "willingness": {"status": "fail", "reason": "refused"},
        "salary": {"status": "pass", "reason": "above_floor"},
    },
    "evidence_anchors": {"salary_text": "£41,000"},
}

EXPECTED_U: dict[str, Any] = {
    "verdict": "UNVERIFIABLE",
    "register_snapshot_date": "2026-08-28",
    "checks": {
        "register": {"status": "pass", "reason": "legal_name_exact"},
        "route": {"status": "pass", "reason": "skilled_worker"},
        "willingness": {"status": "indeterminate", "reason": "silent"},
        "salary": {"status": "pass", "reason": "above_floor"},
    },
}


def _metric(name: str) -> Any:
    return next(m for m in METRICS if m.name == name)


def _cr(
    output: dict[str, Any],
    expected: dict[str, Any],
    payload: dict[str, Any] | None = None,
    error: str | None = None,
) -> CaseResult:
    return CaseResult(
        case_id="t",
        output=output,
        expected=expected,
        seconds=0.01,
        error=error,
        payload=payload if payload is not None else {"requisition_text": POSTING},
    )


def _matching_output(expected: dict[str, Any]) -> dict[str, Any]:
    return {
        "verdict": expected["verdict"],
        "register_snapshot_date": expected["register_snapshot_date"],
        "checks": {k: dict(v) for k, v in expected["checks"].items()},
        "uncertainty": "solver-side field the comparison must ignore",
    }


def test_metric_names_are_the_locked_contract() -> None:
    assert {m.name for m in METRICS} == EXPECTED_METRIC_NAMES


def test_verdict_utility_rewards_correct_verdict() -> None:
    r = _cr({"verdict": "NOT_SPONSORABLE"}, EXPECTED_NS)
    assert _metric("verdict_utility").aggregate([r]) == 1.0


def test_verdict_utility_partial_credit_for_abstention_on_determinable() -> None:
    r = _cr({"verdict": "UNVERIFIABLE"}, EXPECTED_NS)
    assert _metric("verdict_utility").aggregate([r]) == 0.25


def test_verdict_utility_full_credit_for_correct_abstention() -> None:
    r = _cr({"verdict": "UNVERIFIABLE"}, EXPECTED_U)
    assert _metric("verdict_utility").aggregate([r]) == 1.0


def test_verdict_utility_penalises_confident_wrong() -> None:
    r = _cr({"verdict": "SPONSORABLE"}, EXPECTED_NS)
    assert _metric("verdict_utility").aggregate([r]) == -1.0


def test_verdict_utility_scores_missing_verdict_zero() -> None:
    r = _cr({}, EXPECTED_NS, error="RuntimeError: solver crashed")
    assert _metric("verdict_utility").aggregate([r]) == 0.0


def test_confident_wrong_rate_counts_only_definitive_outputs() -> None:
    results = [
        _cr({"verdict": "NOT_SPONSORABLE"}, EXPECTED_NS),  # definitive, right
        _cr({"verdict": "SPONSORABLE"}, EXPECTED_NS),  # definitive, wrong
        _cr({"verdict": "UNVERIFIABLE"}, EXPECTED_NS),  # abstention: excluded
        _cr({}, EXPECTED_NS, error="crash"),  # no verdict: excluded
    ]
    assert _metric("confident_wrong_rate").aggregate(results) == 0.5


def test_check_accuracy_is_a_macro_average_over_the_four_checks() -> None:
    output = _matching_output(EXPECTED_NS)
    output["checks"]["willingness"]["status"] = "indeterminate"  # wrong (truth: fail)
    output["checks"]["salary"]["status"] = "fail"  # wrong (truth: pass)
    assert _metric("check_accuracy").aggregate([_cr(output, EXPECTED_NS)]) == 0.5


def test_check_accuracy_scores_missing_checks_as_misses() -> None:
    assert _metric("check_accuracy").aggregate([_cr({}, EXPECTED_NS)]) == 0.0


def test_exact_match_subset_ignores_label_only_fields() -> None:
    r = _cr(_matching_output(EXPECTED_NS), EXPECTED_NS)
    assert _metric("exact_match").aggregate([r]) == 1.0


def test_exact_match_scores_reason_strictly_when_expected_carries_it() -> None:
    output = _matching_output(EXPECTED_NS)
    output["checks"]["register"]["reason"] = "alias_lookup"  # truth: legal_name_exact
    assert _metric("exact_match").aggregate([_cr(output, EXPECTED_NS)]) == 0.0


def test_exact_match_relaxes_when_reason_is_deleted_from_expected() -> None:
    relaxed = {
        "verdict": EXPECTED_NS["verdict"],
        "register_snapshot_date": EXPECTED_NS["register_snapshot_date"],
        "checks": {
            k: {"status": v["status"]} for k, v in EXPECTED_NS["checks"].items()
        },
    }
    output = _matching_output(EXPECTED_NS)
    output["checks"]["register"]["reason"] = "alias_lookup"  # ignored: not in expected
    assert _metric("exact_match").aggregate([_cr(output, relaxed)]) == 1.0


def test_grounding_verifies_quotes_against_the_posting() -> None:
    grounded = {
        "verdict": "SPONSORABLE",
        "checks": {
            "willingness": {
                "status": "pass",
                "reason": "offered",
                "evidence": {"quote": "We offer visa sponsorship"},
            },
            "salary": {
                "status": "pass",
                "reason": "above_floor",
                "evidence": {"quote": "We happily sponsor everyone"},  # fabricated
            },
        },
    }
    assert _metric("grounding_rate").aggregate([_cr(grounded, EXPECTED_NS)]) == 0.5


def test_grounding_verifies_register_rows_against_the_snapshot() -> None:
    output = {
        "verdict": "NOT_SPONSORABLE",
        "checks": {
            "register": {
                "status": "pass",
                "reason": "legal_name_exact",
                "evidence": {
                    "register_row": {
                        "organisation_name": "Farrowgate Analytics Ltd",
                        "town_city": "London",
                        "type_rating": "Worker (A rating)",
                        "route": "Skilled Worker",
                    }
                },
            },
            "route": {
                "status": "fail",
                "reason": "gbm_only",
                "evidence": {
                    "register_row": {
                        "organisation_name": "Invented Sponsors Ltd",
                        "town_city": "London",
                        "type_rating": "Worker (A rating)",
                        "route": "Skilled Worker",
                    }
                },
            },
        },
    }
    assert _metric("grounding_rate").aggregate([_cr(output, EXPECTED_NS)]) == 0.5


def test_grounding_scores_zero_when_no_citation_is_issued() -> None:
    r = _cr({"verdict": "UNVERIFIABLE", "checks": {}}, EXPECTED_NS)
    assert _metric("grounding_rate").aggregate([r]) == 0.0


def test_cost_per_case_prices_usage_by_model() -> None:
    output = {
        "verdict": "UNVERIFIABLE",
        "_usage": {
            "model": "claude-sonnet-4-6",
            "input_tokens": 1000,
            "output_tokens": 200,
        },
    }
    cost = _metric("cost_per_case_usd").aggregate([_cr(output, EXPECTED_NS)])
    assert cost == (1000 * 3.00 + 200 * 15.00) / 1_000_000


def test_cost_per_case_is_zero_without_usage() -> None:
    assert _metric("cost_per_case_usd").aggregate([_cr({}, EXPECTED_NS)]) == 0.0

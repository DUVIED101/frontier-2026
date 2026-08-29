"""Failing-by-design boundary tests for the rules engine (C-1).

Written the night before the build so Saturday starts red with the shape fixed.
Expectations are hand-derived from the labelling rules in eval/cases/SCHEMA.md and
the committed floor_config.json (T-7) — never from any implementation. Test names
follow the predicate table in docs/PLAN.md §2.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.advanced.rules import (
    CheckOutcome,
    combine,
    salary_clears_floor,
    skilled_worker_route,
    willingness_check,
)

FIXTURES = Path(__file__).resolve().parent.parent / "eval" / "cases" / "fixtures"
FLOOR: dict[str, Any] = json.loads((FIXTURES / "floor_config.json").read_text())

# General threshold £33,400; SOC 2134 new-entrant going rate £38,300 (floor_config).
# A single figure between them is the discriminating band (case-11 archetype); a range
# from below to above the going rate straddles the binding floor.
BETWEEN_THRESHOLDS_GBP = 35_500
BELOW_BOTH_GBP = 29_000
ABOVE_BOTH_MIN_GBP = 39_000
ABOVE_BOTH_MAX_GBP = 44_000
STRADDLE_MIN_GBP = 36_000
STRADDLE_MAX_GBP = 41_000

SKILLED_WORKER_ROUTE = "Skilled Worker"
GBM_ROUTE = "Global Business Mobility: Senior or Specialist Worker"

ALL_PASS: dict[str, CheckOutcome] = {
    "register": CheckOutcome("pass", "legal_name_exact"),
    "route": CheckOutcome("pass", "skilled_worker"),
    "willingness": CheckOutcome("pass", "offered"),
    "salary": CheckOutcome("pass", "above_floor"),
}


def test_salary_below_going_rate_fails() -> None:
    out = salary_clears_floor(BETWEEN_THRESHOLDS_GBP, BETWEEN_THRESHOLDS_GBP, FLOOR)
    assert out == CheckOutcome("fail", "below_going_rate")


def test_salary_below_both_thresholds_fails() -> None:
    out = salary_clears_floor(BELOW_BOTH_GBP, BELOW_BOTH_GBP, FLOOR)
    assert out == CheckOutcome("fail", "below_general_threshold")


def test_salary_range_straddling_floor_is_indeterminate() -> None:
    out = salary_clears_floor(STRADDLE_MIN_GBP, STRADDLE_MAX_GBP, FLOOR)
    assert out == CheckOutcome("indeterminate", "straddles_floor")


def test_salary_above_floor_passes() -> None:
    out = salary_clears_floor(ABOVE_BOTH_MIN_GBP, ABOVE_BOTH_MAX_GBP, FLOOR)
    assert out == CheckOutcome("pass", "above_floor")


def test_salary_absent_is_indeterminate() -> None:
    assert salary_clears_floor(None, None, FLOOR) == CheckOutcome(
        "indeterminate", "absent"
    )


def test_route_skilled_worker_present() -> None:
    out = skilled_worker_route((GBM_ROUTE, SKILLED_WORKER_ROUTE))
    assert out == CheckOutcome("pass", "skilled_worker")


def test_route_gbm_only_fails() -> None:
    assert skilled_worker_route((GBM_ROUTE,)) == CheckOutcome("fail", "gbm_only")


def test_willingness_silence_is_not_refusal() -> None:
    assert willingness_check("silent") == CheckOutcome("indeterminate", "silent")


def test_willingness_right_to_work_boilerplate_is_ambiguous() -> None:
    out = willingness_check("ambiguous")
    assert out == CheckOutcome("indeterminate", "boilerplate_ambiguous")


def test_verdict_all_pass_is_sponsorable() -> None:
    assert combine(dict(ALL_PASS)) == "SPONSORABLE"


def test_verdict_any_fail_is_not_sponsorable() -> None:
    checks = dict(ALL_PASS)
    checks["salary"] = CheckOutcome("fail", "below_going_rate")
    assert combine(checks) == "NOT_SPONSORABLE"


def test_verdict_unresolved_check_is_unverifiable() -> None:
    checks = dict(ALL_PASS)
    checks["willingness"] = CheckOutcome("indeterminate", "silent")
    assert combine(checks) == "UNVERIFIABLE"


def test_verdict_never_sponsorable_without_all_four_evidenced() -> None:
    three_of_four = {k: v for k, v in ALL_PASS.items() if k != "salary"}
    assert combine(three_of_four) == "UNVERIFIABLE"

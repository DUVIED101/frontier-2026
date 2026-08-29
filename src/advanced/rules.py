"""Rules engine: typed claims + resolution -> check outcomes -> verdict.

Pure functions. The salary thresholds come from floor_config, never from a prompt or
a code literal; the verdict comes from the combinator, never from a model — code
decides, the model extracts (Condition C, trajectory 2026-08-29).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

from src.advanced.extract import Stance

Status = Literal["pass", "fail", "indeterminate"]
Verdict = Literal["SPONSORABLE", "NOT_SPONSORABLE", "UNVERIFIABLE"]

CHECK_NAMES = ("register", "route", "willingness", "salary")
SKILLED_WORKER = "Skilled Worker"
GBM_PREFIX = "Global Business Mobility"

_STANCE_OUTCOMES: dict[Stance, tuple[Status, str]] = {
    "offered": ("pass", "offered"),
    "refused": ("fail", "refused"),
    "silent": ("indeterminate", "silent"),
    "ambiguous": ("indeterminate", "boilerplate_ambiguous"),
}


@dataclass(frozen=True)
class CheckOutcome:
    status: Status
    reason: str


def skilled_worker_route(routes: tuple[str, ...]) -> CheckOutcome:
    if not routes:
        return CheckOutcome("indeterminate", "no_entity")
    if any(r == SKILLED_WORKER for r in routes):
        return CheckOutcome("pass", "skilled_worker")
    if all(r.startswith(GBM_PREFIX) for r in routes):
        return CheckOutcome("fail", "gbm_only")
    return CheckOutcome("fail", "other_routes_only")


def willingness_check(stance: Stance) -> CheckOutcome:
    status, reason = _STANCE_OUTCOMES[stance]
    return CheckOutcome(status, reason)


def salary_clears_floor(
    basic_annual_min_gbp: int | None,
    basic_annual_max_gbp: int | None,
    floor_config: dict[str, Any],
    note: str | None = None,
) -> CheckOutcome:
    low = (
        basic_annual_min_gbp
        if basic_annual_min_gbp is not None
        else basic_annual_max_gbp
    )
    high = (
        basic_annual_max_gbp
        if basic_annual_max_gbp is not None
        else basic_annual_min_gbp
    )
    if low is None or high is None:
        # A stated-but-unusable rate (day rate, OTE) carries a currency amount; a
        # bare number inside benefits prose ("4x basic salary") does not — the
        # any-digit rule misdirected the user to ask the wrong question (live
        # finding, 2026-08-29). Wrong reason means wrong advice in the report.
        if note and re.search(r"[£$€]\s*\d", note):
            return CheckOutcome("indeterminate", "non_annual_unclear")
        return CheckOutcome("indeterminate", "absent")
    general = int(floor_config["general_threshold_gbp"]["amount"])
    going = int(floor_config["going_rate_gbp"]["amount"])
    binding = max(general, going)
    if high < binding:
        reason = "below_general_threshold" if high < general else "below_going_rate"
        return CheckOutcome("fail", reason)
    if low >= binding:
        return CheckOutcome("pass", "above_floor")
    return CheckOutcome("indeterminate", "straddles_floor")


def combine(checks: dict[str, CheckOutcome]) -> Verdict:
    outcomes = [checks[name] for name in CHECK_NAMES if name in checks]
    if any(c.status == "fail" for c in outcomes):
        return "NOT_SPONSORABLE"
    if len(outcomes) == len(CHECK_NAMES) and all(c.status == "pass" for c in outcomes):
        return "SPONSORABLE"
    return "UNVERIFIABLE"

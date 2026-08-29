"""Rules engine: typed claims + resolution -> check outcomes -> verdict.

Pure functions. The salary thresholds come from floor_config, never from a prompt or
a code literal; the verdict comes from the combinator, never from a model — code
decides, the model extracts (Condition C, trajectory 2026-08-29). Boundaries pinned
the night before the build.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from src.advanced.extract import Stance

Status = Literal["pass", "fail", "indeterminate"]
Verdict = Literal["SPONSORABLE", "NOT_SPONSORABLE", "UNVERIFIABLE"]


@dataclass(frozen=True)
class CheckOutcome:
    status: Status
    reason: str


def skilled_worker_route(routes: tuple[str, ...]) -> CheckOutcome:
    raise NotImplementedError("stage boundary pinned 2026-08-29; built Saturday")


def willingness_check(stance: Stance) -> CheckOutcome:
    raise NotImplementedError("stage boundary pinned 2026-08-29; built Saturday")


def salary_clears_floor(
    basic_annual_min_gbp: int | None,
    basic_annual_max_gbp: int | None,
    floor_config: dict[str, Any],
) -> CheckOutcome:
    raise NotImplementedError("stage boundary pinned 2026-08-29; built Saturday")


def combine(checks: dict[str, CheckOutcome]) -> Verdict:
    raise NotImplementedError("stage boundary pinned 2026-08-29; built Saturday")

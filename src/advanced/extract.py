"""Extraction stage: requisition text -> typed claims.

The only stage that calls the model. It returns what the posting SAYS — employer
strings, sponsorship stance with its quote, guaranteed-basic salary figures separated
from extras — never what any of it MEANS for the verdict. Interpretation lives in the
rules engine reading floor_config: no threshold or route logic in any prompt
(Condition C, trajectory 2026-08-29). Boundaries pinned the night before the build;
bodies are Saturday morning's work.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Stance = Literal["offered", "refused", "silent", "ambiguous"]


@dataclass(frozen=True)
class StanceClaim:
    stance: Stance
    quote: str | None


@dataclass(frozen=True)
class SalaryClaim:
    """Guaranteed basic gross annual pay only; extras stay out of the figures.

    None on both bounds means no usable annual basic figure was stated; `note`
    carries what the posting said instead (day rate, OTE, "competitive", ...).
    """

    basic_annual_min_gbp: int | None
    basic_annual_max_gbp: int | None
    note: str | None


@dataclass(frozen=True)
class ExtractedClaims:
    employer_strings: tuple[str, ...]
    stance: StanceClaim
    salary: SalaryClaim


def extract_claims(requisition_text: str) -> ExtractedClaims:
    raise NotImplementedError("stage boundary pinned 2026-08-29; built Saturday")

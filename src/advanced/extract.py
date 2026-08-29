"""Extraction stage: requisition text -> typed claims.

The only stage that touches the model, and even here the module holds only the pure
seam — the prompt builder and the reply parser/validator; the API call itself lives
in solve.py so I/O stays at the edge (C-4). The prompt asks what the posting SAYS —
employer strings, sponsorship stance with its verbatim quote, guaranteed-basic salary
figures separated from extras — never what any of it means for the verdict.
Thresholds and route semantics live in the rules engine reading floor_config
(Condition C, trajectory 2026-08-29).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal, cast

Stance = Literal["offered", "refused", "silent", "ambiguous"]
_STANCES: tuple[Stance, ...] = ("offered", "refused", "silent", "ambiguous")


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


def build_extraction_prompt(requisition_text: str) -> tuple[str, str]:
    system = """You read one job posting and report only what it states, as data. \
Reply with ONLY one JSON object, no other text:

{"employer_strings": ["..."], "stance": {"stance": "...", "quote": "..."}, \
"salary": {"basic_annual_min_gbp": 0, "basic_annual_max_gbp": 0, "note": "..."}}

1. "employer_strings": every distinct way the posting names the hiring employer — \
brand names, legal names, any "X is a trading name of Y" statement (list both X and \
Y), and where an agency or aggregator posts on behalf of a client, the client. The \
name the posting primarily uses for the employer comes FIRST; legal or alternative \
names it states come after. Never include a name that does not appear in the text; \
never include the job board itself unless it is the employer.
2. "stance": the posting's position on visa sponsorship for THIS role. "offered" \
only if sponsorship is affirmatively available. "refused" only if the posting \
explicitly states sponsorship is not available, not offered, or that candidates \
needing sponsorship will not be considered. A requirement that applicants have or \
hold the right to work commits to neither — visa sponsorship itself confers that \
right — so such wording alone is "ambiguous", never "refused". "silent" if the \
posting does not mention sponsorship or work eligibility at all. "quote" is the \
verbatim substring the classification rests on, or null when the stance is "silent".
3. "salary": guaranteed basic gross annual pay in GBP only — bonuses, commission, \
OTE, equity, allowances and benefits are not basic pay. A single stated figure fills \
both bounds; a range fills min and max. If basic annual pay is absent, stated in \
non-annual units, or stated only as OTE, set both bounds to null and say in "note" \
what the posting actually stated. "note" is null otherwise."""
    user = f"Posting (as pasted):\n{requisition_text}"
    return system, user


def _int_or_none(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"extract: salary bound is not a number: {value!r}")
    return int(value)


def parse_claims(reply: str) -> ExtractedClaims:
    start, end = reply.find("{"), reply.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("extract: model reply contains no JSON object")
    try:
        raw = json.loads(reply[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(f"extract: model reply is not valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("extract: model reply is not a JSON object")
    try:
        employers = tuple(str(s) for s in raw["employer_strings"])
        stance_value = raw["stance"]["stance"]
        if stance_value not in _STANCES:
            raise ValueError(f"extract: unknown stance {stance_value!r}")
        quote = raw["stance"].get("quote")
        salary = raw["salary"]
        claims = ExtractedClaims(
            employer_strings=employers,
            stance=StanceClaim(
                cast(Stance, stance_value),
                str(quote) if quote is not None else None,
            ),
            salary=SalaryClaim(
                _int_or_none(salary.get("basic_annual_min_gbp")),
                _int_or_none(salary.get("basic_annual_max_gbp")),
                str(salary["note"]) if salary.get("note") is not None else None,
            ),
        )
    except (KeyError, TypeError) as exc:
        raise ValueError(f"extract: malformed claims object: {exc}") from exc
    return claims

"""Unit tests for the extraction stage's deterministic seam (T-2).

The model call itself is exercised by the eval run. What is pinned here: the reply
parser/validator turns well-formed JSON into typed claims and raises a typed error on
anything else (C-5) — never a silent default."""

from __future__ import annotations

import pytest

from src.advanced.extract import (
    ExtractedClaims,
    SalaryClaim,
    StanceClaim,
    parse_claims,
)

VALID_REPLY = """{
  "employer_strings": ["Loopwork", "Ashcombe Digital Ltd"],
  "stance": {"stance": "offered", "quote": "We offer visa sponsorship"},
  "salary": {"basic_annual_min_gbp": 39000, "basic_annual_max_gbp": 44000, "note": null}
}"""


def test_extract_parse_returns_typed_claims() -> None:
    assert parse_claims(VALID_REPLY) == ExtractedClaims(
        employer_strings=("Loopwork", "Ashcombe Digital Ltd"),
        stance=StanceClaim("offered", "We offer visa sponsorship"),
        salary=SalaryClaim(39_000, 44_000, None),
    )


def test_extract_parse_raises_on_unknown_stance() -> None:
    bad = VALID_REPLY.replace('"offered"', '"enthusiastic"')
    with pytest.raises(ValueError):
        parse_claims(bad)


def test_extract_parse_raises_on_garbage() -> None:
    with pytest.raises(ValueError):
        parse_claims("no json here")


WRAPPED_SOURCE = (
    "Benefits include pension. We will sponsor a Skilled\n"
    "Worker visa for the successful applicant; HR handles the CoS process."
)


def test_canonicalize_maps_a_wrapped_quote_to_the_source_bytes() -> None:
    from src.advanced.extract import canonicalize_quote

    unwrapped = "We will sponsor a Skilled Worker visa for the successful applicant"
    span = canonicalize_quote(unwrapped, WRAPPED_SOURCE)
    assert span == "We will sponsor a Skilled\nWorker visa for the successful applicant"
    assert span in WRAPPED_SOURCE


def test_canonicalize_returns_a_verbatim_quote_unchanged() -> None:
    from src.advanced.extract import canonicalize_quote

    verbatim = "HR handles the CoS process"
    assert canonicalize_quote(verbatim, WRAPPED_SOURCE) == verbatim


def test_canonicalize_returns_none_for_fabricated_text() -> None:
    from src.advanced.extract import canonicalize_quote

    assert canonicalize_quote("We happily sponsor everyone", WRAPPED_SOURCE) is None
    assert canonicalize_quote(None, WRAPPED_SOURCE) is None

"""Failing-by-design boundary tests for entity resolution (C-1).

Row and alias values come from the committed fixture vocabulary
(register_fixture_rows.json, aliases.json) so the contract is exercised on exactly
the entities the eval cases use. Expectations hand-derived from the C1 predicate in
docs/PLAN.md §2 (T-7)."""

from __future__ import annotations

import json
from pathlib import Path

from src.advanced.resolve import (
    Ambiguous,
    Match,
    NoMatch,
    RegisterRow,
    resolve_entity,
)

FIXTURES = Path(__file__).resolve().parent.parent / "eval" / "cases" / "fixtures"
ALIASES: dict[str, str] = json.loads((FIXTURES / "aliases.json").read_text())["aliases"]

ASHCOMBE = RegisterRow(
    "Ashcombe Digital Ltd", "London", "", "Worker (A rating)", "Skilled Worker"
)
HALCYON_TECH = RegisterRow(
    "Halcyon Technologies Ltd", "London", "", "Worker (A rating)", "Skilled Worker"
)
HALCYON_CONSULTING = RegisterRow(
    "Halcyon Consulting (UK) Ltd", "London", "", "Worker (A rating)", "Skilled Worker"
)
ROWS = (ASHCOMBE, HALCYON_TECH, HALCYON_CONSULTING)

UNLISTED = "Fictional Unlisted Co"


def test_register_exact_legal_name_matches() -> None:
    result = resolve_entity(("Ashcombe Digital Ltd",), ROWS, {})
    assert result == Match("Ashcombe Digital Ltd", (ASHCOMBE,))


def test_register_legal_suffix_variation_still_matches() -> None:
    result = resolve_entity(("Ashcombe Digital Limited",), ROWS, {})
    assert result == Match("Ashcombe Digital Ltd", (ASHCOMBE,))


def test_register_trading_name_resolves_to_legal_entity() -> None:
    result = resolve_entity(("Loopwork",), ROWS, ALIASES)
    assert result == Match("Ashcombe Digital Ltd", (ASHCOMBE,))


def test_register_unlisted_employer_is_no_match() -> None:
    result = resolve_entity((UNLISTED,), ROWS, ALIASES)
    assert isinstance(result, NoMatch)


def test_register_ambiguous_multi_entity_is_indeterminate() -> None:
    result = resolve_entity(("Halcyon",), ROWS, {})
    assert isinstance(result, Ambiguous)
    assert set(result.organisation_names) == {
        "Halcyon Technologies Ltd",
        "Halcyon Consulting (UK) Ltd",
    }


# The genericity threshold counts distinct ORGANISATIONS a string matches; a matched
# entity's own rows are never capped. The baseline conflates both concerns in one
# constant (frozen, left alone); these two tests pin the separation (2026-08-29
# checkpoint). MANY_ROWS exceeds the baseline's excerpt cap of 20 on purpose.
MANY_ROWS = 25


def test_resolver_returns_all_rows_of_a_large_matched_entity_uncapped() -> None:
    routes = ("Skilled Worker", "Global Business Mobility: Senior or Specialist Worker")
    large_org = tuple(
        RegisterRow(
            "Bryelock Systems Ltd", f"Town {i}", "", "Worker (A rating)", routes[i % 2]
        )
        for i in range(MANY_ROWS)
    )
    result = resolve_entity(("Bryelock Systems Ltd",), large_org + ROWS, {})
    assert result == Match("Bryelock Systems Ltd", large_org)


def test_resolver_skips_a_string_matching_more_orgs_than_the_generic_limit() -> None:
    from src.advanced.resolve import GENERIC_TERM_ORG_LIMIT

    generic_orgs = tuple(
        RegisterRow(
            f"Consulting {i} Ltd", "London", "", "Worker (A rating)", "Skilled Worker"
        )
        for i in range(GENERIC_TERM_ORG_LIMIT + 1)
    )
    result = resolve_entity(("Consulting",), generic_orgs + ROWS, {})
    assert isinstance(result, NoMatch)

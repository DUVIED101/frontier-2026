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

"""Unit tests for the baseline solver's deterministic parts — no API calls.

The model call itself is exercised by the eval run, not unit tests (T-2). What is
pinned here: the naive register lookup behaves exactly as designed — including its
designed blindness to brand aliases, which is a documented baseline failure mode, not
a defect (docs/PLAN.md §4) — and the prompt states the rules the labels are scored
against (two thresholds, guaranteed-basic-only, output contract).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.baseline.solve import (
    FLOOR,
    SNAPSHOT_DATE,
    build_prompt,
    candidate_strings,
    parse_response,
    register_context,
)

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "eval" / "cases"

MAX_ROWS = 20


def _case_text(name: str) -> str:
    doc = json.loads((CASES / name).read_text())
    return str(doc["payload"]["requisition_text"])


def test_baseline_candidates_include_header_names() -> None:
    text = _case_text("case-02-refusal-licensed.json")
    assert "Farrowgate Analytics Ltd" in candidate_strings(text)
    aggregator = _case_text("case-01-compound-aggregator-gbm.json")
    assert "Ottervale" in candidate_strings(aggregator)


def test_baseline_lookup_finds_exact_legal_name() -> None:
    context = register_context(["Farrowgate Analytics Ltd"])
    assert "Farrowgate Analytics Ltd" in context
    assert "Skilled Worker" in context
    assert context != "NO ROWS MATCHED"


def test_baseline_lookup_is_blind_to_brand_aliases() -> None:
    text = _case_text("case-01-compound-aggregator-gbm.json")
    assert register_context(candidate_strings(text)) == "NO ROWS MATCHED"


def test_baseline_lookup_caps_rows() -> None:
    lines = register_context(["Software"]).splitlines()
    assert len(lines) == MAX_ROWS
    assert all("software" in line.casefold() for line in lines)


def test_baseline_prompt_states_both_thresholds_and_base_pay_rule() -> None:
    system, _ = build_prompt("posting text", "NO ROWS MATCHED")
    general = FLOOR["general_threshold_gbp"]["amount"]
    going = FLOOR["going_rate_gbp"]["amount"]
    assert f"£{general:,}" in system
    assert f"£{going:,}" in system
    assert "guaranteed basic" in system
    for excluded in ("bonus", "profit share", "equity"):
        assert excluded in system


def test_baseline_prompt_includes_output_contract_and_snapshot_date() -> None:
    system, user = build_prompt("the posting body", "the register excerpt")
    for key in ("verdict", "checks", "uncertainty", "register_snapshot_date"):
        assert f'"{key}"' in system
    for check in ("register", "route", "willingness", "salary"):
        assert f'"{check}"' in system
    assert SNAPSHOT_DATE in system
    assert "the posting body" in user
    assert "the register excerpt" in user


def test_baseline_parse_extracts_json_from_prose() -> None:
    reply = 'Here is my assessment:\n{"verdict": "UNVERIFIABLE", "checks": {}}\nThanks!'
    assert parse_response(reply) == {"verdict": "UNVERIFIABLE", "checks": {}}


def test_baseline_parse_raises_on_garbage() -> None:
    with pytest.raises(ValueError):
        parse_response("I cannot answer in JSON, sorry.")

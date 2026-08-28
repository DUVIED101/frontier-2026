"""Fixture-integrity tests for the committed register snapshot and its companions.

These verify the evaluation's ground substrate before any solver exists: fixture rows
exist exactly as the cases anchor them, absence assertions hold against the committed
snapshot in both directions (SCHEMA.md "Fixture-integrity tests"), and no field-level
pattern separates fixture rows from real ones (gate-2 correction 6 and its addition).

Absence is defined as "no match under the resolver's normalisations", so these tests
import the same normalisation module the resolver uses — one definition, not two.
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import re
from pathlib import Path
from typing import Any

import pytest

from src.advanced.normalize import normalize_org_name, token_set

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "eval" / "cases" / "fixtures"
CASES_DIR = ROOT / "eval" / "cases"

SNAPSHOT_GLOB = "sponsor-register-*.csv.gz"
COLUMNS = ["Organisation Name", "Town/City", "County", "Type & Rating", "Route"]
# A shape feature shared by every fixture row must also cover at least this share of
# real rows — a rarer feature would be a learnable separator.
MIN_REAL_POPULATION_SHARE = 0.05
# Alphabetically adjacent fixture names (the two Halcyon and two Merrivale entities)
# may land next to each other; a longer run would mean appending, not inserting.
MAX_CONSECUTIVE_FIXTURE_ROWS = 2


def _snapshot_path() -> Path:
    matches = sorted(FIXTURES.glob(SNAPSHOT_GLOB))
    assert matches, f"no register snapshot under {FIXTURES}"
    return matches[-1]


@pytest.fixture(scope="module")
def snapshot_text() -> str:
    return gzip.decompress(_snapshot_path().read_bytes()).decode("utf-8-sig")


@pytest.fixture(scope="module")
def register_rows(snapshot_text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(snapshot_text)))


@pytest.fixture(scope="module")
def manifest() -> dict[str, Any]:
    return json.loads((FIXTURES / "register_fixture_rows.json").read_text())


@pytest.fixture(scope="module")
def aliases() -> dict[str, Any]:
    return json.loads((FIXTURES / "aliases.json").read_text())


@pytest.fixture(scope="module")
def cases() -> list[dict[str, Any]]:
    files = sorted(CASES_DIR.glob("*.json"))
    assert files, "no case files"
    return [json.loads(f.read_text()) for f in files]


def _fixture_names(manifest: dict[str, Any]) -> set[str]:
    return {r["organisation_name"] for r in manifest["rows"]}


def _split_rows(
    register_rows: list[dict[str, str]], manifest: dict[str, Any]
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    names = _fixture_names(manifest)
    real = [r for r in register_rows if r["Organisation Name"] not in names]
    fixture = [r for r in register_rows if r["Organisation Name"] in names]
    return real, fixture


def test_fixture_orgs_do_not_collide_with_real_register(
    register_rows: list[dict[str, str]], manifest: dict[str, Any]
) -> None:
    real, _ = _split_rows(register_rows, manifest)
    real_norms = {normalize_org_name(r["Organisation Name"]) for r in real}
    real_token_sets = {token_set(r["Organisation Name"]) for r in real}
    collisions = {
        name
        for name in _fixture_names(manifest)
        if normalize_org_name(name) in real_norms or token_set(name) in real_token_sets
    }
    assert collisions == set()


def test_asserted_absent_names_match_no_row_under_any_normalisation(
    register_rows: list[dict[str, str]],
    manifest: dict[str, Any],
    aliases: dict[str, Any],
    cases: list[dict[str, Any]],
) -> None:
    asserted = {
        name for c in cases for name in c["meta"].get("asserted_absent_names", [])
    }
    assert asserted, "no absence assertions found in any case"
    all_norms = {normalize_org_name(r["Organisation Name"]) for r in register_rows}
    all_token_sets = {token_set(r["Organisation Name"]) for r in register_rows}
    alias_norms = {
        normalize_org_name(s)
        for s in [*aliases["aliases"].keys(), *aliases["aliases"].values()]
    }
    hits = {
        name
        for name in asserted
        if normalize_org_name(name) in all_norms
        or token_set(name) in all_token_sets
        or normalize_org_name(name) in alias_norms
    }
    assert hits == set()


def test_fixture_rows_use_real_register_vocabulary(
    register_rows: list[dict[str, str]], manifest: dict[str, Any]
) -> None:
    real, fixture = _split_rows(register_rows, manifest)
    real_ratings = {r["Type & Rating"] for r in real}
    real_routes = {r["Route"] for r in real}
    real_towns = {r["Town/City"] for r in real}
    counties_by_town: dict[str, set[str]] = {}
    for r in real:
        counties_by_town.setdefault(r["Town/City"], set()).add(r["County"])
    for r in fixture:
        assert r["Type & Rating"] in real_ratings, r
        assert r["Route"] in real_routes, r
        assert r["Town/City"] in real_towns, r
        assert r["County"] in counties_by_town[r["Town/City"]], r


def test_fixture_rows_are_shape_indistinguishable(
    snapshot_text: str, register_rows: list[dict[str, str]], manifest: dict[str, Any]
) -> None:
    real, fixture = _split_rows(register_rows, manifest)
    assert len(fixture) == len(manifest["rows"])

    lines = snapshot_text.split("\r\n")
    assert lines[0].split(",") == COLUMNS
    assert lines[-1] == "", "file must end with CRLF like the source"

    names = _fixture_names(manifest)
    fixture_lines = [ln for ln in lines[1:-1] if ln.split(",")[0] in names]
    assert len(fixture_lines) == len(manifest["rows"])
    for ln in fixture_lines:
        assert ln.count(",") == len(COLUMNS) - 1, ln
        assert '"' not in ln, ln

    mixed_case_real = sum(1 for r in real if not r["Organisation Name"].isupper())
    tidy_real = sum(1 for r in real if all(r[c] == r[c].strip() for c in COLUMNS))
    for share in (mixed_case_real / len(real), tidy_real / len(real)):
        assert share >= MIN_REAL_POPULATION_SHARE
    for r in fixture:
        assert not r["Organisation Name"].isupper(), r
        assert all(r[c] == r[c].strip() for c in COLUMNS), r

    indices = [i for i, ln in enumerate(lines[1:-1]) if ln.split(",")[0] in names]
    run, longest = 1, 1
    for prev, cur in zip(indices, indices[1:]):
        run = run + 1 if cur == prev + 1 else 1
        longest = max(longest, run)
    assert longest <= MAX_CONSECUTIVE_FIXTURE_ROWS
    n_data = len(lines) - 2
    assert indices[0] < n_data * 0.2 and indices[-1] > n_data * 0.8, (
        "fixture rows must be spread through the file, not clustered"
    )


def test_case_register_anchors_match_fixture_rows_verbatim(
    register_rows: list[dict[str, str]],
    manifest: dict[str, Any],
    cases: list[dict[str, Any]],
) -> None:
    manifest_rows = {
        (r["organisation_name"], r["town_city"], r["type_rating"], r["route"])
        for r in manifest["rows"]
    }
    snapshot_rows = {
        (r["Organisation Name"], r["Town/City"], r["Type & Rating"], r["Route"])
        for r in register_rows
    }
    anchored = [
        c["expected"]["evidence_anchors"]["register_row"]
        for c in cases
        if "register_row" in c["expected"].get("evidence_anchors", {})
    ]
    assert anchored, "no register_row anchors found"
    for a in anchored:
        key = (a["organisation_name"], a["town_city"], a["type_rating"], a["route"])
        assert key in manifest_rows, a
        assert key in snapshot_rows, a


def test_alias_fixtures_resolve_to_manifest_entities(
    manifest: dict[str, Any], aliases: dict[str, Any]
) -> None:
    names = _fixture_names(manifest)
    assert aliases["aliases"] == {
        "Ottervale": "Bryelock Systems Ltd",
        "Loopwork": "Ashcombe Digital Ltd",
    }
    assert set(aliases["aliases"].values()) <= names


def test_snapshot_date_consistent_across_cases_and_fixtures(
    manifest: dict[str, Any], cases: list[dict[str, Any]]
) -> None:
    date = manifest["snapshot_date"]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", date)
    assert date in _snapshot_path().name
    mismatched = {
        c["id"] for c in cases if c["expected"]["register_snapshot_date"] != date
    }
    assert mismatched == set()


def test_register_row_counts_match_manifest(
    register_rows: list[dict[str, str]], manifest: dict[str, Any]
) -> None:
    assert len(register_rows) == manifest["real_row_count"] + len(manifest["rows"])

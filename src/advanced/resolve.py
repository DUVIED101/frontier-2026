"""Entity resolution: employer strings -> register entity. Deterministic only.

Normalisation, token-set matching and the committed alias fixtures; no model call
anywhere in this stage. NoMatch is definitive only after the full alias pass, and
more than one surviving entity is Ambiguous, never a guess (C1 policy, docs/PLAN.md
§2).

Two concerns the baseline conflates in one constant are separate here (2026-08-29
checkpoint): GENERIC_TERM_ORG_LIMIT counts distinct ORGANISATIONS a candidate string
matches — above it the string is a generic word, not a name, and is skipped. A
matched entity's own rows are returned UNCAPPED: how many rows an excerpt should
carry is the renderer's concern, and a real organisation can legitimately hold more
rows than any excerpt would show.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass

from src.advanced.normalize import normalize_org_name, token_set

GENERIC_TERM_ORG_LIMIT = 20


@dataclass(frozen=True)
class RegisterRow:
    organisation_name: str
    town_city: str
    county: str
    type_rating: str
    route: str


@dataclass(frozen=True)
class Match:
    organisation_name: str
    rows: tuple[RegisterRow, ...]


@dataclass(frozen=True)
class NoMatch:
    searched: tuple[str, ...]


@dataclass(frozen=True)
class Ambiguous:
    organisation_names: tuple[str, ...]


Resolution = Match | NoMatch | Ambiguous


@functools.lru_cache(maxsize=8)
def _org_index(
    register_rows: tuple[RegisterRow, ...],
) -> tuple[dict[str, tuple[str, ...]], tuple[tuple[str, frozenset[str]], ...]]:
    """Normalised-name -> organisation names, plus (org, token-set) pairs.

    Keyed by the rows tuple itself so tests with synthetic registers and the real
    snapshot coexist; the tuple is hashable and loaded once per register.
    """
    by_norm: dict[str, list[str]] = {}
    tokens: dict[str, frozenset[str]] = {}
    for row in register_rows:
        org = row.organisation_name
        if org not in tokens:
            by_norm.setdefault(normalize_org_name(org), []).append(org)
            tokens[org] = token_set(org)
    return (
        {norm: tuple(orgs) for norm, orgs in by_norm.items()},
        tuple(tokens.items()),
    )


def _rows_of(
    org: str, register_rows: tuple[RegisterRow, ...]
) -> tuple[RegisterRow, ...]:
    return tuple(r for r in register_rows if r.organisation_name == org)


def resolve_entity(
    employer_strings: tuple[str, ...],
    register_rows: tuple[RegisterRow, ...],
    aliases: dict[str, str],
) -> Resolution:
    by_norm, org_tokens = _org_index(register_rows)
    searched: list[str] = []
    for raw in employer_strings:
        for candidate in (raw, aliases.get(raw, "")):
            if not candidate or candidate in searched:
                continue
            searched.append(candidate)
            exact = by_norm.get(normalize_org_name(candidate), ())
            if len(exact) == 1:
                return Match(exact[0], _rows_of(exact[0], register_rows))
            if len(exact) > 1:
                return Ambiguous(exact)
            needle = token_set(candidate)
            if not needle:
                continue
            partial = tuple(org for org, toks in org_tokens if needle <= toks)
            if len(partial) > GENERIC_TERM_ORG_LIMIT:
                continue
            if len(partial) == 1:
                return Match(partial[0], _rows_of(partial[0], register_rows))
            if len(partial) > 1:
                return Ambiguous(partial)
    return NoMatch(tuple(searched))

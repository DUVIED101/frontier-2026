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
from typing import Literal

from src.advanced.normalize import normalize_org_name, token_set

GENERIC_TERM_ORG_LIMIT = 20


@dataclass(frozen=True)
class RegisterRow:
    organisation_name: str
    town_city: str
    county: str
    type_rating: str
    route: str


ResolutionVia = Literal["legal_name_exact", "trading_name_stated", "alias_lookup"]


@dataclass(frozen=True)
class Match:
    organisation_name: str
    rows: tuple[RegisterRow, ...]
    via: ResolutionVia


@dataclass(frozen=True)
class NoMatch:
    searched: tuple[str, ...]


@dataclass(frozen=True)
class Ambiguous:
    """More than one surviving entity — and everything known about each of them.

    The candidate rows travel with the ambiguity so the report can tell the user
    exactly what diverges; evidence a stage produces must reach the user unless
    there is a reason it should not (review pattern, 2026-08-29)."""

    organisation_names: tuple[str, ...]
    rows: tuple[RegisterRow, ...]


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
    """Three phases, and the winning phase names the register reason.

    Every posting-stated string is tried before any alias (C1: the posting's own
    words outrank external fixtures): exact-normalised match over all strings,
    then token-subset over all strings, then the alias pass. A match on the
    posting's primary string is `legal_name_exact`; on a later stated string,
    `trading_name_stated`; via the alias fixtures, `alias_lookup`.
    """
    by_norm, org_tokens = _org_index(register_rows)
    searched: list[str] = []

    def _ambiguous(orgs: tuple[str, ...]) -> Ambiguous:
        rows = tuple(r for org in orgs for r in _rows_of(org, register_rows))
        return Ambiguous(orgs, rows)

    def _exact(candidate: str) -> tuple[str, ...]:
        return by_norm.get(normalize_org_name(candidate), ())

    def _subset(candidate: str) -> tuple[str, ...]:
        needle = token_set(candidate)
        if not needle:
            return ()
        partial = tuple(org for org, toks in org_tokens if needle <= toks)
        return () if len(partial) > GENERIC_TERM_ORG_LIMIT else partial

    def _via(index: int) -> ResolutionVia:
        return "legal_name_exact" if index == 0 else "trading_name_stated"

    for finder in (_exact, _subset):
        for i, raw in enumerate(employer_strings):
            if not raw:
                continue
            if raw not in searched:
                searched.append(raw)
            orgs = finder(raw)
            if len(orgs) == 1:
                return Match(orgs[0], _rows_of(orgs[0], register_rows), _via(i))
            if len(orgs) > 1:
                return _ambiguous(orgs)
    for raw in employer_strings:
        candidate = aliases.get(raw, "")
        if not candidate or candidate in searched:
            continue
        searched.append(candidate)
        for finder in (_exact, _subset):
            orgs = finder(candidate)
            if len(orgs) == 1:
                return Match(orgs[0], _rows_of(orgs[0], register_rows), "alias_lookup")
            if len(orgs) > 1:
                return _ambiguous(orgs)
    return NoMatch(tuple(searched))

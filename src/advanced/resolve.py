"""Entity resolution: employer strings -> register entity. Deterministic only.

Normalisation, fuzzy token-set matching and the committed alias fixtures; no model
call anywhere in this stage. NoMatch is definitive only after the full alias pass,
and more than one surviving entity is Ambiguous, never a guess (C1 policy,
docs/PLAN.md §2). Boundaries pinned the night before the build.
"""

from __future__ import annotations

from dataclasses import dataclass


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


def resolve_entity(
    employer_strings: tuple[str, ...],
    register_rows: tuple[RegisterRow, ...],
    aliases: dict[str, str],
) -> Resolution:
    raise NotImplementedError("stage boundary pinned 2026-08-29; built Saturday")

"""Organisation-name normalisation for entity resolution against the sponsor register.

tests/test_fixture_integrity.py defines absence as "no match under these
normalisations", so the resolver and the integrity tests must share this one
definition — do not fork it.
"""

from __future__ import annotations

import re

# Tokens that vary between a posting's rendering of an employer and the register's
# legal name without changing identity. Validated against the 2026-08-28 snapshot:
# zero fictional-name collisions under this exact list.
_LEGAL_TOKENS = frozenset(
    {"ltd", "limited", "plc", "llp", "llc", "inc", "uk", "holdings", "group", "ta"}
)


def normalize_org_name(name: str) -> str:
    """Casefold, strip punctuation, and drop legal-form tokens.

    "t/a" is collapsed before punctuation stripping so it cannot survive as the
    stray tokens "t", "a".
    """
    s = name.casefold().strip().replace("t/a", " ")
    s = re.sub(r"[^\w\s]", " ", s)
    tokens = [t for t in s.split() if t not in _LEGAL_TOKENS]
    return " ".join(tokens)


def token_set(name: str) -> frozenset[str]:
    """Order-insensitive form of the normalised name, for token-set comparison."""
    return frozenset(normalize_org_name(name).split())

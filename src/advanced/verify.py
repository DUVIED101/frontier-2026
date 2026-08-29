"""Verification stage: mechanically re-check evidence; downgrade what fails.

Every quote must be a verbatim substring of the source; anything unsupported drops
the check to indeterminate so the combinator can only move toward UNVERIFIABLE,
never toward a confident verdict (docs/PLAN.md §5). This is the mechanical core;
the evening pass wires it into the pipeline and extends it to register-row gates.
"""

from __future__ import annotations

from src.advanced.rules import CheckOutcome

UNVERIFIED_REASON = "evidence_unverified"


def verify_and_downgrade(
    checks: dict[str, CheckOutcome],
    quotes: dict[str, str | None],
    source_text: str,
) -> dict[str, CheckOutcome]:
    out: dict[str, CheckOutcome] = {}
    for name, outcome in checks.items():
        quote = quotes.get(name)
        if quote is not None and quote not in source_text:
            out[name] = CheckOutcome("indeterminate", UNVERIFIED_REASON)
        else:
            out[name] = outcome
    return out

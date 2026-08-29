"""Verification stage: mechanically re-check evidence; downgrade what fails.

Every quote must be a verbatim substring of the source; anything unsupported drops
the check to indeterminate so the combinator can only move toward UNVERIFIABLE,
never toward a confident verdict (docs/PLAN.md §5). Saturday-evening scope; the
boundary is pinned now so the pipeline is wired against it from the start.
"""

from __future__ import annotations

from src.advanced.rules import CheckOutcome


def verify_and_downgrade(
    checks: dict[str, CheckOutcome],
    quotes: dict[str, str | None],
    source_text: str,
) -> dict[str, CheckOutcome]:
    raise NotImplementedError("stage boundary pinned 2026-08-29; built Saturday")

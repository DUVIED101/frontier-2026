"""Baseline solution — deliberately simple reference implementation.

FROZEN after its first green evaluation run (CLAUDE.md CN-3). Do not edit, do not
refactor, do not share code with src/advanced/. Every reported improvement is measured
against this file exactly as it stands.
"""

from __future__ import annotations

from typing import Any


def solve(payload: dict[str, Any], *, seed: int = 42) -> dict[str, Any]:
    """Simplest thing that could possibly work. Implement after kickoff.

    Aim for something a competent engineer would write in under an hour with no
    cleverness: a single obvious pass, no retries, no tuning. It exists to be beaten.
    """
    raise NotImplementedError("baseline: implement after kickoff")

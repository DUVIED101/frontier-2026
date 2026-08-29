"""Unit tests for the removed-experiment variant's pure voting logic (T-2).

The sampling itself is exercised by the eval run; what is pinned here is the vote:
strict majority wins, and disagreement without a majority abstains — the experiment
must never manufacture confidence out of a split (hand-derived expectations, T-7)."""

from __future__ import annotations

from src.experiments.self_consistency import vote


def test_vote_strict_majority_wins() -> None:
    verdicts = ("NOT_SPONSORABLE", "NOT_SPONSORABLE", "SPONSORABLE")
    assert vote(verdicts) == "NOT_SPONSORABLE"


def test_vote_unanimity_wins() -> None:
    verdicts = ("SPONSORABLE", "SPONSORABLE", "SPONSORABLE")
    assert vote(verdicts) == "SPONSORABLE"


def test_vote_three_way_split_abstains() -> None:
    verdicts = ("SPONSORABLE", "NOT_SPONSORABLE", "UNVERIFIABLE")
    assert vote(verdicts) == "UNVERIFIABLE"


def test_vote_empty_after_parse_failures_abstains() -> None:
    assert vote(()) == "UNVERIFIABLE"

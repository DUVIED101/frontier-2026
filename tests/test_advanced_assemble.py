"""Unit tests for the pure assembly seam of the advanced pipeline (T-2).

assemble() verifies model-sourced quotes against the posting text before the
combinator runs (loop 2): a fabricated quote downgrades its check to indeterminate
and is stripped from evidence, so the verdict can only move toward UNVERIFIABLE.

The model call is exercised by the eval; assemble() is deterministic given typed
claims and a resolution, so its behaviour on the two policy-critical shapes is
pinned here with hand-derived expectations (T-7): register presence must not imply
sponsorability (route decides), and silence must block SPONSORABLE without producing
NOT_SPONSORABLE (C3 policy, docs/PLAN.md §2)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.advanced.extract import ExtractedClaims, SalaryClaim, StanceClaim
from src.advanced.resolve import Match, RegisterRow
from src.advanced.solve import assemble

FIXTURES = Path(__file__).resolve().parent.parent / "eval" / "cases" / "fixtures"
FLOOR: dict[str, Any] = json.loads((FIXTURES / "floor_config.json").read_text())
SNAPSHOT_DATE = "2026-08-28"
POSTING = "Join us. We offer visa sponsorship. Salary £46,000."

GBM_ONLY_ROW = RegisterRow(
    "Veltrix Software Ltd",
    "London",
    "",
    "Worker (A rating)",
    "Global Business Mobility: Senior or Specialist Worker",
)
SW_ROW = RegisterRow(
    "Ostermere Technologies Ltd", "London", "", "Worker (A rating)", "Skilled Worker"
)


def test_assemble_register_presence_does_not_imply_sponsorability() -> None:
    claims = ExtractedClaims(
        employer_strings=("Veltrix Software Ltd",),
        stance=StanceClaim("offered", "We offer visa sponsorship"),
        salary=SalaryClaim(46_000, 46_000, None),
    )
    out = assemble(
        claims,
        Match("Veltrix Software Ltd", (GBM_ONLY_ROW,), "legal_name_exact"),
        FLOOR,
        SNAPSHOT_DATE,
        POSTING,
    )
    assert out["verdict"] == "NOT_SPONSORABLE"
    assert out["checks"]["register"]["status"] == "pass"
    assert out["checks"]["route"] == {
        "status": "fail",
        "reason": "gbm_only",
        "evidence": {
            "register_row": {
                "organisation_name": "Veltrix Software Ltd",
                "town_city": "London",
                "type_rating": "Worker (A rating)",
                "route": "Global Business Mobility: Senior or Specialist Worker",
            }
        },
    }


def test_assemble_silence_blocks_sponsorable_without_producing_not_sponsorable() -> (
    None
):
    claims = ExtractedClaims(
        employer_strings=("Ostermere Technologies Ltd",),
        stance=StanceClaim("silent", None),
        salary=SalaryClaim(42_000, 42_000, None),
    )
    out = assemble(
        claims,
        Match("Ostermere Technologies Ltd", (SW_ROW,), "legal_name_exact"),
        FLOOR,
        SNAPSHOT_DATE,
        POSTING,
    )
    assert out["verdict"] == "UNVERIFIABLE"
    assert out["checks"]["willingness"] == {
        "status": "indeterminate",
        "reason": "silent",
    }
    assert out["register_snapshot_date"] == SNAPSHOT_DATE
    assert "willingness" in out["uncertainty"]


# The B-rating sub-check is deliberately cut (scope ruling 2026-08-29): the rating
# never changes a verdict, but a non-A rating must surface in the uncertainty
# statement — a B-rated sponsor cannot issue a CoS until its action plan completes,
# and "nothing material left unresolved" would overstate confidence (PLAN §8 cut
# order; case-28 archetype).
B_RATED_SW_ROW = RegisterRow(
    "Duncastle Tech Ltd", "London", "", "Worker (B rating)", "Skilled Worker"
)


def test_assemble_surfaces_non_a_rating_in_uncertainty_without_changing_verdict() -> (
    None
):
    claims = ExtractedClaims(
        employer_strings=("Duncastle Tech Ltd",),
        stance=StanceClaim("offered", "We offer visa sponsorship"),
        salary=SalaryClaim(42_000, 42_000, None),
    )
    out = assemble(
        claims,
        Match("Duncastle Tech Ltd", (B_RATED_SW_ROW,), "legal_name_exact"),
        FLOOR,
        SNAPSHOT_DATE,
        POSTING,
    )
    assert out["verdict"] == "SPONSORABLE"
    assert "Worker (B rating)" in out["uncertainty"]
    assert "rating" in out["uncertainty"]


def test_assemble_stays_quiet_about_a_rated_licences() -> None:
    claims = ExtractedClaims(
        employer_strings=("Ostermere Technologies Ltd",),
        stance=StanceClaim("offered", "We offer visa sponsorship"),
        salary=SalaryClaim(42_000, 42_000, None),
    )
    out = assemble(
        claims,
        Match("Ostermere Technologies Ltd", (SW_ROW,), "legal_name_exact"),
        FLOOR,
        SNAPSHOT_DATE,
        POSTING,
    )
    assert out["verdict"] == "SPONSORABLE"
    assert out["uncertainty"] == "nothing material left unresolved"


def test_assemble_downgrades_fabricated_stance_quote_and_recomputes_verdict() -> None:
    claims = ExtractedClaims(
        employer_strings=("Ostermere Technologies Ltd",),
        stance=StanceClaim("offered", "We happily sponsor everyone"),
        salary=SalaryClaim(46_000, 46_000, None),
    )
    out = assemble(
        claims,
        Match("Ostermere Technologies Ltd", (SW_ROW,), "legal_name_exact"),
        FLOOR,
        SNAPSHOT_DATE,
        POSTING,
    )
    assert out["verdict"] == "UNVERIFIABLE"
    assert out["checks"]["willingness"] == {
        "status": "indeterminate",
        "reason": "evidence_unverified",
    }
    assert "willingness" in out["uncertainty"]


def test_assemble_repairs_a_wrapped_quote_to_the_source_span() -> None:
    wrapped_posting = (
        "Join us. Salary £46,000. We will sponsor a Skilled\n"
        "Worker visa for the successful applicant."
    )
    claims = ExtractedClaims(
        employer_strings=("Ostermere Technologies Ltd",),
        stance=StanceClaim(
            "offered",
            "We will sponsor a Skilled Worker visa for the successful applicant",
        ),
        salary=SalaryClaim(46_000, 46_000, None),
    )
    out = assemble(
        claims,
        Match("Ostermere Technologies Ltd", (SW_ROW,), "legal_name_exact"),
        FLOOR,
        SNAPSHOT_DATE,
        wrapped_posting,
    )
    assert out["verdict"] == "SPONSORABLE"
    assert out["checks"]["willingness"]["status"] == "pass"
    quote = out["checks"]["willingness"]["evidence"]["quote"]
    assert "\n" in quote
    assert quote in wrapped_posting


MULTI_ROUTE_ROWS = (
    RegisterRow(
        "Quillhaven Systems Ltd",
        "London",
        "",
        "Temporary Worker (A rating)",
        "Creative Worker",
    ),
    RegisterRow(
        "Quillhaven Systems Ltd", "London", "", "Worker (A rating)", "Skilled Worker"
    ),
)


def test_assemble_cites_the_row_the_verdict_rests_on_for_multi_route_entities() -> None:
    claims = ExtractedClaims(
        employer_strings=("Quillhaven Systems Ltd",),
        stance=StanceClaim("offered", "We offer visa sponsorship"),
        salary=SalaryClaim(43_000, 43_000, None),
    )
    out = assemble(
        claims,
        Match("Quillhaven Systems Ltd", MULTI_ROUTE_ROWS, "legal_name_exact"),
        FLOOR,
        SNAPSHOT_DATE,
        POSTING,
    )
    assert out["verdict"] == "SPONSORABLE"
    register_ev = out["checks"]["register"]["evidence"]
    assert register_ev["register_row"]["route"] == "Skilled Worker"
    assert register_ev["routes_held"] == ["Creative Worker", "Skilled Worker"]


def test_ambiguity_note_groups_candidates_by_licence_route() -> None:
    from src.advanced.resolve import Ambiguous

    rows = (
        RegisterRow(
            "Zephyr Data Ltd", "Leeds", "", "Worker (A rating)", "Skilled Worker"
        ),
        RegisterRow(
            "Zephyr Labs Ltd", "York", "", "Worker (A rating)", "Skilled Worker"
        ),
        RegisterRow(
            "Zephyr Mobility Ltd",
            "Hull",
            "",
            "Worker (A rating)",
            "Global Business Mobility: Senior or Specialist Worker",
        ),
    )
    claims = ExtractedClaims(
        employer_strings=("Zephyr",),
        stance=StanceClaim("offered", "We offer visa sponsorship"),
        salary=SalaryClaim(46_000, 46_000, None),
    )
    out = assemble(
        claims,
        Ambiguous(("Zephyr Data Ltd", "Zephyr Labs Ltd", "Zephyr Mobility Ltd"), rows),
        FLOOR,
        SNAPSHOT_DATE,
        POSTING,
    )
    assert out["uncertainty_notes"][0] == (
        "3 register entities match the posted employer. By licence route — "
        "Skilled Worker: Zephyr Data Ltd, Zephyr Labs Ltd; "
        "Global Business Mobility: Senior or Specialist Worker: "
        "Zephyr Mobility Ltd. Which one would issue the Certificate of "
        "Sponsorship decides whether this role can sponsor at all"
    )

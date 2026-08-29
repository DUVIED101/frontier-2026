"""The six named report properties from docs/PLAN.md §5b (T-4), red before the build.

render_report is a pure function over the solver's output dict and the posting text —
no LLM in the render path (DECISIONS.md 2026-08-28). Every expectation is
hand-derived from the §5b contents list (T-7)."""

from __future__ import annotations

from typing import Any

from src.advanced.report import render_report

SNAPSHOT_DATE = "2026-08-28"
POSTING = "Join Farrowgate. We offer visa sponsorship for this role. Salary £41,000."
QUOTE = "We offer visa sponsorship for this role"

ROW = {
    "organisation_name": "Farrowgate Analytics Ltd",
    "town_city": "London",
    "type_rating": "Worker (A rating)",
    "route": "Skilled Worker",
}


def _result(verdict: str, checks: dict[str, Any], determining: str) -> dict[str, Any]:
    return {
        "verdict": verdict,
        "determining_fact": determining,
        "checks": checks,
        "uncertainty": "built by assemble; the report derives its own section",
        "register_snapshot_date": SNAPSHOT_DATE,
    }


ALL_PASS_CHECKS: dict[str, Any] = {
    "register": {
        "status": "pass",
        "reason": "legal_name_exact",
        "evidence": {"register_row": dict(ROW)},
    },
    "route": {
        "status": "pass",
        "reason": "skilled_worker",
        "evidence": {"register_row": dict(ROW)},
    },
    "willingness": {
        "status": "pass",
        "reason": "offered",
        "evidence": {"quote": QUOTE},
    },
    "salary": {"status": "pass", "reason": "above_floor"},
}


def test_report_leads_with_verdict_and_determining_sentence() -> None:
    determining = "All four checks pass against the register snapshot and floor config."
    report = render_report(
        _result("SPONSORABLE", ALL_PASS_CHECKS, determining), POSTING
    )
    lines = report.splitlines()
    assert lines[0] == "VERDICT: SPONSORABLE"
    assert lines[1] == f"Why: {determining}"


def test_report_quote_offsets_are_valid_spans_of_source() -> None:
    report = render_report(_result("SPONSORABLE", ALL_PASS_CHECKS, "d."), POSTING)
    marker = "chars "
    assert marker in report
    line = next(ln for ln in report.splitlines() if marker in ln)
    span = line.split(marker)[1].split(":")[0]
    start, end = (int(x) for x in span.split("-"))
    assert POSTING[start:end] == QUOTE


def test_report_reproduces_register_row_verbatim() -> None:
    report = render_report(_result("SPONSORABLE", ALL_PASS_CHECKS, "d."), POSTING)
    for value in ROW.values():
        assert value in report


def test_report_states_snapshot_date_and_age_warning() -> None:
    report = render_report(_result("SPONSORABLE", ALL_PASS_CHECKS, "d."), POSTING)
    assert SNAPSHOT_DATE in report
    assert "revoked and suspended continuously" in report
    assert "only as fresh as that snapshot" in report


def test_report_uncertainty_names_each_unresolved_check() -> None:
    checks = {
        "register": dict(ALL_PASS_CHECKS["register"]),
        "route": dict(ALL_PASS_CHECKS["route"]),
        "willingness": {"status": "indeterminate", "reason": "silent"},
        "salary": {"status": "indeterminate", "reason": "absent"},
    }
    report = render_report(
        _result("UNVERIFIABLE", checks, "Cannot be verified."), POSTING
    )
    section = report.split("Could not be established")[1]
    assert "Sponsorship for this role" in section
    assert "Salary floor" in section
    assert section.count("To resolve:") == 2


def test_report_closes_with_advisory_line() -> None:
    report = render_report(_result("SPONSORABLE", ALL_PASS_CHECKS, "d."), POSTING)
    assert report.rstrip().endswith(
        "This report is advisory. The evidence above is checkable; "
        "whether to apply is your decision."
    )


def test_report_never_claims_completeness_while_uncertainty_notes_remain() -> None:
    result = _result("SPONSORABLE", ALL_PASS_CHECKS, "d.")
    result["uncertainty_notes"] = [
        "licence rating not assessed: the register shows Worker (B rating); "
        "a sponsor rated below A cannot issue a Certificate of Sponsorship "
        "until its action plan completes"
    ]
    report = render_report(result, POSTING)
    assert "Nothing material was left unresolved" not in report
    assert "Worker (B rating)" in report


def test_report_cites_a_shared_register_row_once() -> None:
    report = render_report(_result("SPONSORABLE", ALL_PASS_CHECKS, "d."), POSTING)
    assert report.count("Farrowgate Analytics Ltd") == 1
    assert "as cited under Sponsor register" in report


def test_report_names_every_candidate_entity_when_resolution_is_ambiguous() -> None:
    from src.advanced.extract import ExtractedClaims, SalaryClaim, StanceClaim
    from src.advanced.resolve import Ambiguous, RegisterRow
    from src.advanced.solve import assemble

    diverging = (
        RegisterRow(
            "Halcyon Technologies Ltd",
            "London",
            "",
            "Worker (A rating)",
            "Skilled Worker",
        ),
        RegisterRow(
            "Halcyon Consulting (UK) Ltd",
            "London",
            "",
            "Worker (A rating)",
            "Global Business Mobility: Senior or Specialist Worker",
        ),
    )
    claims = ExtractedClaims(
        employer_strings=("Halcyon Group",),
        stance=StanceClaim("offered", QUOTE),
        salary=SalaryClaim(44_000, 44_000, None),
    )
    result = assemble(
        claims,
        Ambiguous(
            ("Halcyon Technologies Ltd", "Halcyon Consulting (UK) Ltd"), diverging
        ),
        {
            "general_threshold_gbp": {"amount": 33400},
            "going_rate_gbp": {"amount": 38300},
        },
        SNAPSHOT_DATE,
        POSTING,
    )
    report = render_report(result, POSTING)
    assert "Halcyon Technologies Ltd" in report
    assert "Halcyon Consulting (UK) Ltd" in report
    assert "Skilled Worker" in report
    assert "Global Business Mobility" in report

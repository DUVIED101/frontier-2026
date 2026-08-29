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
